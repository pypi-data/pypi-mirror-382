#ifndef LAYERTPP
#define LAYERTPP

#include "layer.hpp"

#include <cblas.h>

#include <arm_neon.h>

#include <chrono>
#include <random>

inline auto make_seed() {
    std::random_device rd; 
    auto time = std::chrono::high_resolution_clock::now()
                    .time_since_epoch().count();

    std::seed_seq seq{ rd(),
                       static_cast<unsigned>(time & 0xFFFFFFFF),
                       static_cast<unsigned>(time >> 32) };
    std::mt19937 gen(seq); 
    return gen;
}

template <typename NumType>
Layer<NumType>::Layer(size_t prev_layer, size_t this_layer, bool momentumVal)
: 
dis(-sqrt(6.0f/(prev_layer+this_layer)), sqrt(6.0f/(prev_layer+this_layer)))
{
    gen = make_seed();
    biases = Array<NumType, 1>(this_layer);
    weight_inner_size = this_layer;
    size_t weightShape[2] = {prev_layer, this_layer};
    weights = Array<NumType, 2>(weightShape);
    for(size_t i = 0; i < this_layer; i++){
        biases[i] = 0.0f;
    }
    for(size_t i = 0; i < prev_layer; i++){
        for(size_t j = 0; j < this_layer; j++){
            weights[i][j]= 0.5f*dis(gen);
        }
    }
    momentum = momentumVal;
}

template <typename NumType>
Layer<NumType>::~Layer()
{
    for (auto p : inputsRL)   { delete p; }
    for (auto p : outputsRL)  { delete p; }

    inputsRL.clear();
    outputsRL.clear();

}


template <typename NumType>
Layer<NumType>::Layer(Layer&& other) noexcept
    : inputSave(std::move(other.inputSave)),
      momentum(other.momentum),
      gen(std::move(other.gen)),
      dis(std::move(other.dis)),
      inputsRL(std::move(other.inputsRL)),
      outputsRL(std::move(other.outputsRL)),
      dinputs(std::move(other.dinputs)),
      biases(std::move(other.biases)),
      weights(std::move(other.weights)),
      outputs(std::move(other.outputs)),
      dweights(std::move(other.dweights)),
      dbiases(std::move(other.dbiases)),
      weight_inner_size(other.weight_inner_size)
{
    other.inputsRL.clear();
    other.outputsRL.clear();
}

template <typename NumType>
Layer<NumType>& Layer<NumType>::operator=(Layer&& other) noexcept
{
    if (this != &other) {
        inputSave = std::move(other.inputSave);
        momentum = other.momentum;
        gen = std::move(other.gen);
        dis = std::move(other.dis);

        inputsRL = std::move(other.inputsRL);
        outputsRL = std::move(other.outputsRL);

        dinputs = std::move(other.dinputs);
        biases = std::move(other.biases);
        weights = std::move(other.weights);
        outputs = std::move(other.outputs);
        dweights = std::move(other.dweights);
        dbiases = std::move(other.dbiases);
        weight_inner_size = other.weight_inner_size;

        other.inputsRL.clear();
        other.outputsRL.clear();
    }
    return *this;
}
/*
template <typename NumType>
Array<NumType, 2> Layer<NumType>::forward(const Array<NumType, 2>& input) {
    size_t outputsShape[2] = { input.shape[0], biases.len };
    outputs = Array<NumType, 2>(outputsShape);

    size_t arr[2] = { input.shape[0], weights.shape[0] };
    inputSave = Array<NumType, 2>(arr);

    for (size_t k = 0; k < input.shape[0]; ++k) {
        for (size_t i = 0; i < biases.len; ++i) {
            outputs.fastSet2D(k, i, 0.0f);
            for (size_t j = 0; j < weights.shape[0]; ++j) {
                outputs.data[outputs.stride[0]*k+ i]+= input.data[k*input.stride[0]+j] * weights.data[weights.stride[0]*j+ i];
                inputSave.data[k*inputSave.stride[0]+j] = input.data[k*input.stride[0]+ j];
            }
            outputs.fastInc2D(k, i,biases[i]);
        }
    }
    return outputs;
}

*/
    //data[i*stride[0]+j*stride[1]] += val;
    //data[i*stride[0]+j*stride[1]] = val;
    //return data[i*stride[0]+j*stride[1]];

template <typename NumType>
Array<NumType, 2> Layer<NumType>::forward(Array<NumType, 2> const& input){
    size_t outputsShape[2] = {input.shape[0], biases.len};
    outputs = Array<NumType, 2>(outputsShape);
    size_t arr[2] = {input.shape[0], weights.shape[0]};
    inputSave = Array<NumType, 2>(arr);

    if(input.shape[1]!= weights.shape[0]){
        return Array<NumType, 2>();
    }
    /*Stopwatch w;
    size_t M = input.shape[0];
    size_t K = input.shape[1];
    size_t N = biases.len;        

    cblas_dgemm(CblasRowMajor,
                CblasNoTrans,       
                CblasTrans,        
                M, N, K,
                1.0,
                input.data,   K,   
                weights.data, K,   
                0.0,
                outputs.data, N);   
    auto gemmc = w.elapsed();
    std::cout << "BLAS: " <<  gemmc << std::endl;
    w.reset();*/
    double * weightsdata = weights.data;
    size_t weightsstride0 = weights.stride[0];
    double * inputdata = input.data;
    size_t sizes[2];
    sizes[1] = weights.shape[0];
    sizes[0] = weights.shape[1];
    Array<double, 2> weightsT = Array<double, 2>(sizes);
    for(size_t i = 0; i < sizes[0]; i++){
        for(size_t j = 0; j < sizes[1]; j++){
            weightsT.fastSet2D(i, j, weights.fastGet2D(j, i));
        }
    }
    //std::cout << weights.shape[0] << ", "<< weights.shape[1] << "\n" << weightsT.shape[0] << ", "<< weightsT.shape[1] << std::endl;
    size_t weightsshape0 = weights.shape[0];
    double * weightsTdata = weightsT.data;
    for(size_t k = 0; k < input.shape[0]; k++){                
        size_t input_inner = k*input.stride[0];
        double * curinputdata = &inputdata[input_inner];
        size_t inputSave_inner = k*inputSave.stride[0];
        size_t output_inner = k*outputs.stride[0];
        for(size_t i = 0; i < biases.len; i++){
            size_t output_loc = output_inner+i;
            size_t weights_outer = i*weightsT.stride[0];
            double * curweightsTdata = &weightsTdata[weights_outer];
            outputs.data[output_loc] = 0.0f;

            float64x2_t accs[6] = {vdupq_n_f64(0.0), vdupq_n_f64(0.0), 
            vdupq_n_f64(0.0), vdupq_n_f64(0.0), vdupq_n_f64(0.0), vdupq_n_f64(0.0)};

            //double accs[8] = {};

            size_t j = 0;
            for(; j+11 < weightsshape0; j+=12){
                //outputs.data[output_loc] += weights.data[j*weights.stride[0]+weights_outer];
                //(k, i, input.fastGet2D(k, j) * weights.fastGet2D(j, i));
                __builtin_prefetch(curweightsTdata + j + 64, 0, 1);
                __builtin_prefetch(curinputdata + j + 64, 0, 1);
                
                float64x2_t nextinputs1 = vld1q_f64(curinputdata+j);
                float64x2_t nextweights1 = vld1q_f64(curweightsTdata+j);
                accs[0] = vfmaq_f64(accs[0], nextinputs1, nextweights1);

                float64x2_t nextinputs2 = vld1q_f64(curinputdata + j +  2);
                float64x2_t nextweights2 = vld1q_f64(curweightsTdata + j +  2);
                accs[1] = vfmaq_f64(accs[1], nextinputs2, nextweights2);

                float64x2_t nextinputs3 = vld1q_f64(curinputdata + j +  4);
                float64x2_t nextweights3 = vld1q_f64(curweightsTdata + j +  4);
                accs[2] = vfmaq_f64(accs[2], nextinputs3, nextweights3);

                float64x2_t nextinputs4 = vld1q_f64(curinputdata + j +  6);
                float64x2_t nextweights4 = vld1q_f64(curweightsTdata + j +  6);
                accs[3] = vfmaq_f64(accs[3], nextinputs4, nextweights4);

                float64x2_t nextinputs5 = vld1q_f64(curinputdata + j +  8);
                float64x2_t nextweights5 = vld1q_f64(curweightsTdata + j +  8);
                accs[4] = vfmaq_f64(accs[4], nextinputs5, nextweights5);

                float64x2_t nextinputs6 = vld1q_f64(curinputdata + j +  10);
                float64x2_t nextweights6 = vld1q_f64(curweightsTdata + j +  10);
                accs[5] = vfmaq_f64(accs[5], nextinputs6, nextweights6);

                
                /*auto off = j+weights_outer;
                accs[0] += curinputdata[j] * weightsTdata[off];
                off++;
                accs[1] += curinputdata[ (j+1)] * weightsdata[off];
                off++;
                accs[2] += curinputdata[ (j+2)] * weightsdata[off];
                off ++;
                accs[3] += curinputdata[ (j+3)] * weightsdata[off];
                off ++;
                accs[4] += curinputdata[ (j+4)] * weightsdata[off];
                off ++;

                accs[5] += curinputdata[ (j+5)] * weightsdata[off];
                off ++;

                accs[6] += curinputdata[ (j+6)] * weightsdata[off];
                off ++;

                accs[7] += curinputdata[ (j+7)] * weightsdata[off];*/

                
                //fastSet2D(k, j, input.fastGet2D(k, j));
                
            }
            for(; j < weights.shape[0]; j++){
                outputs.data[output_loc] += curinputdata[j] * curweightsTdata[j];
            }

            outputs.data[output_loc] +=      vaddvq_f64(accs[0]) +
                                            vaddvq_f64(accs[1]) +
                                            vaddvq_f64(accs[2]) +
                                            vaddvq_f64(accs[3]) + vaddvq_f64(accs[4]) +
                                            vaddvq_f64(accs[5]);
            //outputs.data[output_loc] += accs[0] + accs[1] + accs[2] + accs[3] + accs[4] + accs[5] + accs[6] + accs[7];
            outputs.data[output_loc] +=  biases.data[i*biases.stride];

        }



    }
    //auto x = w.elapsed();
    //std::cout << "My Code: " << x << "\n" <<  "Blas is " << (x/gemmc)<<  "times faster than me"<< std::endl;

        for(size_t k = 0; k < input.shape[0]; k++){                
        size_t input_inner = k*input.stride[0];
        double * curinputdata = &inputdata[input_inner];
        size_t inputSave_inner = k*inputSave.stride[0];
        size_t output_inner = k*outputs.stride[0];


                for(size_t j = 0; j < weights.shape[0]; j++){
                inputSave.data[inputSave_inner+j] = input.data[input_inner+j];
                /*inputSave.data[inputSave_inner+(j+1)*inputSave.stride[1]] = input.data[input_inner+(j+1)*inputSave.stride[1]];
                inputSave.data[inputSave_inner+(j+2)*inputSave.stride[1]] = input.data[input_inner+(j+2)*inputSave.stride[1]];
                inputSave.data[inputSave_inner+(j+3)*inputSave.stride[1]] = input.data[input_inner+(j+3)*inputSave.stride[1]];
                inputSave.data[inputSave_inner+(j+4)*inputSave.stride[1]] = input.data[input_inner+(j+4)*inputSave.stride[1]];
                inputSave.data[inputSave_inner+(j+5)*inputSave.stride[1]] = input.data[input_inner+(j+5)*inputSave.stride[1]];*/
            }
            }/*
    size_t N = biases.len;
size_t K = weightsshape0;

for (size_t k = 0; k < input.shape[0]; ++k) {
    const double* curinputdata = inputdata + k * input.stride[0];
    size_t output_inner = k * outputs.stride[0];

    size_t i = 0;
    for (; i + 3 < N; i += 4) {
        float64x2_t acc0 = vdupq_n_f64(0.0);
        float64x2_t acc1 = vdupq_n_f64(0.0);
        float64x2_t acc2 = vdupq_n_f64(0.0);
        float64x2_t acc3 = vdupq_n_f64(0.0);

        const double* w0 = weightsTdata + (i+0)*K;
        const double* w1 = weightsTdata + (i+1)*K;
        const double* w2 = weightsTdata + (i+2)*K;
        const double* w3 = weightsTdata + (i+3)*K;

        size_t j = 0;
        for (; j + 1 < K; j += 2) {
            float64x2_t xv  = vld1q_f64(curinputdata + j);
            acc0 = vfmaq_f64(acc0, xv, vld1q_f64(w0 + j));
            acc1 = vfmaq_f64(acc1, xv, vld1q_f64(w1 + j));
            acc2 = vfmaq_f64(acc2, xv, vld1q_f64(w2 + j));
            acc3 = vfmaq_f64(acc3, xv, vld1q_f64(w3 + j));
        }

        double sum0 = vaddvq_f64(acc0);
        double sum1 = vaddvq_f64(acc1);
        double sum2 = vaddvq_f64(acc2);
        double sum3 = vaddvq_f64(acc3);

        for (; j < K; ++j) {
            double xj = curinputdata[j];
            sum0 += xj * w0[j];
            sum1 += xj * w1[j];
            sum2 += xj * w2[j];
            sum3 += xj * w3[j];
        }

        outputs.data[output_inner + i+0] = sum0 + biases.data[i+0];
        outputs.data[output_inner + i+1] = sum1 + biases.data[i+1];
        outputs.data[output_inner + i+2] = sum2 + biases.data[i+2];
        outputs.data[output_inner + i+3] = sum3 + biases.data[i+3];
    }

    // tail outputs
    for (; i < N; ++i) {
        double sum = 0.0;
        const double* w = weightsTdata + i*K;
        for (size_t j = 0; j < K; ++j)
            sum += curinputdata[j] * w[j];
        outputs.data[output_inner + i] = sum + biases.data[i];
    }
}*/

    return outputs;
}

template <typename NumType>
Array<NumType, 1> Layer<NumType>::forwardRL(Array<NumType, 1> const& input){
    auto* in = new Array<NumType, 1>(weights.shape[0]);
    auto* out = new Array<NumType, 1>(biases.len);

    for(int i = 0; i < in->len; i++){
        (*in)[i] = input[i];
    }
    for(int i = 0; i < biases.len; i++){
        (*out)[i] = biases[i];
        for(int j = 0; j < weights.shape[0]; j++){
            (*out)[i] += (*in)[j] * weights[j][i];
        }
    }
    inputsRL.push_back(in);
    outputsRL.push_back(out);
    return (*out); // FIX WHEN MOVE CONSTRUCTOR IS ADDED TO ARRAY CLASS I KNOW IT SHOULD ALREADY EXIST DON'T JUDGE ME
}

template <typename NumType>
Array<NumType, 1> Layer<NumType>::forwardGA(Array<NumType, 1> const& input){
    auto* in = new Array<NumType, 1>(weights.shape[0]);
    auto* out = new Array<NumType, 1>(biases.len);

    for(int i = 0; i < in->len; i++){
        (*in)[i] = input[i];
    }
    for(int i = 0; i < biases.len; i++){
        (*out)[i] = biases[i];
        for(int j = 0; j < weights.shape[0]; j++){
            (*out)[i] += (*in)[j] * weights[j][i];
        }
    }
    return (*out); // FIX WHEN MOVE CONSTRUCTOR IS ADDED TO ARRAY CLASS I KNOW IT SHOULD ALREADY EXIST DON'T JUDGE ME
}

template <typename NumType>
void Layer<NumType>::endEpisodeRL(){
    size_t epSize = inputsRL.size();
    size_t inArr[2] = {epSize, weights.shape[0]};
    inputSave = Array<NumType, 2>(inArr);
    size_t outArr[2] = {epSize, biases.len};
    outputs = Array<NumType, 2>(outArr);
    for(size_t i = 0; i < epSize; i++){
        for(size_t j = 0; j < weights.shape[0]; j++){
            inputSave[i][j] = (*inputsRL[i])[j];
        }
        for(size_t j = 0; j < biases.len; j++){
            outputs[i][j] = (*outputsRL[i])[j];
        }
        delete inputsRL[i];
        delete outputsRL[i];
    }
    inputsRL.clear();
    outputsRL.clear();
}

template <typename NumType>
Array<NumType, 2> Layer<NumType>::backward(Array<NumType, 2>& dvalues){
    dbiases = Array<NumType, 1>(biases.len);
    for(size_t j = 0; j < biases.len; j++){
            dbiases.data[j] = dvalues.data[dvalues.stride[1]*j];
    }

    for(size_t i = 1; i < dvalues.shape[0]; i++){ // colARowB
        for(size_t j = 0; j < weight_inner_size; j++){ // colB
            dbiases.data[j] += dvalues.data[i*dvalues.stride[0]+j*dvalues.stride[1]];
        }
    }


    size_t sizes[2] = {inputSave.shape[1], dvalues.shape[1]};
    dweights = Array<NumType, 2>(sizes);
    for(size_t i = 0; i < inputSave.shape[1]; i++){
        auto off = i*dweights.stride[0];
        for(size_t j = 0; j < dvalues.shape[1]; j++){
            dweights.data[off+j] = 0;
        }
    }

    /*for(size_t k = 0; k < inputSave.shape[0]; k++){
        auto inputSave_outer =  k*inputSave.stride[0];
        auto dvalues_outer = k*dvalues.stride[0];
        for(size_t j = 0; j < inputSave.shape[1]; j++){

            size_t inputSave_loc = inputSave_outer+j*inputSave.stride[1];
            size_t dweights_outer = j*dweights.stride[0];
            double accs[8] = {};
            for(size_t i = 0; i +7 < dvalues.shape[1]; i+=8){
                dweights.data[dweights_outer+i] += inputSave.data[inputSave_loc]* dvalues.data[dvalues_outer+i*dvalues.stride[1]];
            }
        }
    }*/
    size_t inF  = inputSave.shape[1];
    size_t outF = dvalues.shape[1];
    size_t B    = inputSave.shape[0];

    cblas_dgemm(
    CblasRowMajor, CblasTrans, CblasNoTrans,
    inF,               outF,     B,
    1.0,
    inputSave.data,   inputSave.stride[0],
    dvalues.data,     dvalues.stride[0],
    0.0,
    dweights.data,          dweights.stride[0]);

    //dweights = (inputSave.transpose()) * dvalues;

    //Stopwatch w;
    size_t sizes2[2] = {dvalues.shape[0], weights.shape[0]};
    auto dinputs = Array<NumType, 2>(sizes2);
    for(size_t i = 0; i < dvalues.shape[0]; i++){
        auto off = i*dinputs.stride[0];
        for(size_t j = 0; j < weights.shape[0]; j++){
            dinputs.data[off+j] = 0;
        }
    }
    const int B2 = dvalues.shape[0]; 
    const int O = dvalues.shape[1];  
    const int I = weights.shape[0]; 

    const int lda = dvalues.stride[0];   
    const int ldb = weights.stride[0];  
    const int ldc = dinputs.stride[0]; 

    cblas_dgemm(
        CblasRowMajor,   
        CblasNoTrans,   
        CblasTrans,  
        B2, 
        I, 
        O,   
        1.0, 
        dvalues.data,  lda, 
        weights.data, ldb, 
        0.0,     
        dinputs.data, ldc); 

    //auto r = dvalues * (weights.transpose());
    return dinputs;

}

template <typename NumType>
void Layer<NumType>::randomize(NumType strength){
    std::uniform_real_distribution<NumType> weightRandomizer(-strength, strength);
    for(size_t i = 0; i < weights.shape[0]; i++){
        for(size_t j = 0; j < weights.shape[1]; j++){
            weights[i][j] += weightRandomizer(gen);
            if(weights[i][j] > 1){
                weights[i][j] = 1;
            }
            else if(weights[i][j] < -1){
                weights[i][j] = -1;
            }

        }
    }
    for(size_t i = 0; i <biases.len; i++){
        biases[i] += weightRandomizer(gen);
        if(biases[i] > 1){
            biases[i] = 1;
        }
        else if (biases[i] < -1){
            biases[i] = -1;
        }
    }
}

template <typename NumType>
void Layer<NumType>::deepcopy(const Layer<NumType>* other){
    for(size_t i = 0; i < weights.shape[0]; i++){
        for(size_t j = 0; j < weights.shape[1]; j++){
            weights[i][j] = other->weights[i][j];
        }
    }
    for(size_t i = 0; i < biases.len; i++){
        biases[i] = other->biases[i];
    }
    return;
}

#endif
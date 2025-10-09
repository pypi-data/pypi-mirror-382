#ifndef ACTIVATIONSOFTMAX_H
#define ACTIVATIONSOFTMAX_H
#include <cmath>
#include <iostream>
#include "../utilities/matrixutility.hpp"
#include "baseactivation.hpp"
#include "../../utilities/stopwatch/stopwatch.hpp"

template <typename NumType = float>
class ActivationSoftMax : public BaseActivation<NumType>
{
    private:
        size_t saved_samples;
        size_t saved_prev_layer;
    public:
        ActivationSoftMax(){
            this->type = 0x02;
        }
        Array<NumType, 2> forward(Array<NumType, 2>& inputs, size_t samples, size_t prev_layer) override{
            //matrixViewer(inputs, samples, prev_layer);
            
            saved_samples = inputs.shape[0];
            saved_prev_layer = inputs.shape[1];
            if(saved_samples <= 0){
                return Array<NumType, 2>();
            }
            /*if(this->outputs != nullptr){
                clearMatrix(this->outputs, samples);
                this->outputs = nullptr;
            }*/
            size_t outputsShape[2] = {saved_samples, saved_prev_layer};
            this->outputs = Array<NumType, 2>(outputsShape);
            for(int i = 0; i < saved_samples; i++){
                NumType sum = 0.0f;
                NumType max = inputs[i][0];
                for(int j = 1; j < saved_prev_layer; j++){
                    if(max < inputs[i][j]){
                        max = inputs[i][j];
                    }
                }
                for(int j = 0; j < saved_prev_layer; j++){
                    this->outputs[i][j] = exp(inputs[i][j]-max);
                    sum += this->outputs[i][j];
                }
                for(int j = 0; j < saved_prev_layer; j++){
                    if(i== 0 && j == 0){
                        //std::cout << sum << std::endl;
                    }
                    this->outputs[i][j] = this->outputs[i][j]/(sum+1e-7);
                }
            }
            return this->outputs;
        }

        // MEANT FOR GA 100% NOT GONNA WORK FOR RL
        Array<NumType, 1> forwardRL(Array<NumType, 1>& input) override
        {
            size_t prev_layer = input.len;
            auto output = Array<NumType, 1>(prev_layer);
            NumType sum = 0.0f;
            NumType max = input[0];
            for(int j = 1; j < prev_layer; j++){
                if(max < input[j]){
                    max = input[j];
                }
            }
            for(int j = 0; j < prev_layer; j++){
                output[j] = exp(input[j]-max);
                sum += output[j];
            }
            for(int j = 0; j < prev_layer; j++){
                
                output[j] = output[j]/(sum+1e-7);
            }
        
            return output;
              
        }


        Array<NumType, 2> backward(Array<NumType, 2>& dvalues) override{
            size_t dinputsShape[2] = {saved_samples, saved_prev_layer};
            this->dinputs = Array<NumType, 2>(dinputsShape);
            for(int i = 0; i < saved_samples; i++){
                this->dinputs[i] << dvalsXJacobian(this->outputs[i], saved_prev_layer, dvalues[i]); 
                //std::cout << "DINPUT OF SOFTMAX" << std::endl;
                //std::cout << dinputs[i][0] << std::endl;
            }
            //matrixViewer(dinputs, samples, 2);
            return this->dinputs;
        }


        void print() override{
            std::cout << " Softmax " << std::endl;
        }

        void endEpisodeRL() override
        {
        }

};

#endif
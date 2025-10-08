#ifndef ACTIVATIONRELU_H
#define ACTIVATIONRELU_H

#include "baseactivation.hpp"

template <typename NumType = float>
class ActivationReLU : public BaseActivation<NumType>
{
    private:
        Array<NumType, 2> saved_inputs;
        size_t saved_samples;
        size_t saved_prev_layer;
        NumType minimum;
        std::vector<Array<NumType, 1>*> inputsRL;
        std::vector<Array<NumType, 1>*> outputsRL;
    public:
        ActivationReLU(){
            this->type = 0x01;
            minimum = 0.0f;
        }
        ActivationReLU(NumType minimumVal){
            this->type = 0x01;
            minimum = minimumVal;
        }

        ActivationReLU(const ActivationReLU& other)
            : BaseActivation<NumType>(other),                      
            saved_inputs(other.saved_inputs),
            saved_samples(other.saved_samples),
            saved_prev_layer(other.saved_prev_layer),
            minimum(other.minimum),
            inputsRL(),                                        
            outputsRL()
        {
            this->type = 0x01;
            inputsRL.reserve(other.inputsRL.size());
            outputsRL.reserve(other.outputsRL.size());

            for (auto* ptr : other.inputsRL) {
                if (ptr) {
                    inputsRL.push_back(new Array<NumType, 1>(*ptr));  
                } else {
                    inputsRL.push_back(nullptr);                  
                }
            }

            for (auto* ptr : other.outputsRL) {
                if (ptr) {
                    outputsRL.push_back(new Array<NumType, 1>(*ptr));
                } else {
                    outputsRL.push_back(nullptr);
                }
            }
        }

        ~ActivationReLU(){
            endEpisodeRL();
        }


        Array<NumType, 2> forward(Array<NumType, 2>& inputs, size_t samples, size_t prev_layer) override{
            
            saved_samples = inputs.shape[0];
            saved_prev_layer = inputs.shape[1];
            size_t shape[2] = {saved_samples, saved_prev_layer};
            saved_inputs = Array<NumType, 2>(shape);
            this->outputs = Array<NumType, 2>(shape);
            for(size_t i = 0; i < saved_samples; i++){
                for(size_t j = 0; j < saved_prev_layer; j++){
                    saved_inputs.fastSet2D(i, j, inputs.fastGet2D(i, j));
                    if(inputs.fastGet2D(i, j) < minimum){
                        this->outputs.fastSet2D(i, j, minimum);
                    }
                    else{
                        this->outputs.fastSet2D(i,j, inputs.fastGet2D(i,j));
                    }
                }
            }
            return this->outputs;
        }

        Array<NumType, 1> forwardRL(Array<NumType, 1>& input) override{
            auto* saved = new Array<NumType, 1>(input.len);
            this->saved_prev_layer = input.len;
            auto* out = new Array<NumType, 1>(input.len);
            for (size_t i = 0; i < input.len; i++) {
                (*saved)[i] = input[i];
                (*out)[i] = input[i] < minimum ? minimum : input[i];
            }
            inputsRL.push_back(saved);
            outputsRL.push_back(out); 
            return (*out); 
        }

        void endEpisodeRL() override{
            size_t epSize = inputsRL.size();
            size_t inArr[2] = {epSize, this->saved_prev_layer};
            saved_inputs = Array<NumType, 2>(inArr);  
            size_t outArr[2] =  {epSize, this->saved_prev_layer};
            this->outputs = Array<NumType, 2>(outArr);

            for(int i = 0; i < epSize; i++){
                for(int j = 0; j < saved_prev_layer; j++){
                    saved_inputs[i][j] = (*inputsRL[i])[j];
                    this->outputs[i][j] = (*outputsRL[i])[j];
                }
                delete inputsRL[i];
                delete outputsRL[i];
            }
            saved_samples = epSize;
            inputsRL.clear();
            outputsRL.clear();
        }

        Array<NumType, 2> backward(Array<NumType, 2>& dvalues) override{

            size_t dinputsShape[2] = {saved_samples, saved_prev_layer};
            this->dinputs = Array<NumType, 2>(dinputsShape);

            
            for(size_t i = 0; i < saved_samples; i++){
                for(size_t j = 0; j < saved_prev_layer; j++){
                    if(saved_inputs[i][j] <= 0){
                        this->dinputs[i][j] = 0;
                    }
                    else{
                        this->dinputs[i][j] = dvalues[i][j];
                    }
                }
            }
            return this->dinputs.copy();
        }
        void print() override{
            std::cout << " ReLU " << std::endl;
        }

};

#endif
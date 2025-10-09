#ifndef ArbitraryActivation_TPP
#define ArbitraryActivation_TPP

#include "arbitraryactivation.hpp"
#include "../../matrix/matrix.hpp"
#include <cstdint>

// WHEN WRAPPED TO PYTHON YOU DO NOT OWN OUTPUTS OUTPUTS WILL BE KILLED BY THE PYTHON INTERPRETER IF LOGITS = OUTPUTS SAVE INPUTS IF AN ACTIVATION NEEDS BOTH SAVE BOTH

template <typename NumType>
Array<NumType, 2>* activationForward(Array<NumType, 2>* inputs, ActivationLayer<NumType>& layer){
    // Switch to binary search after 4-6 activations are finished
    // ReLU Arbitrary Minimum
    if(layer.type == 0x0){
            void* mem = std::malloc(sizeof(Array<NumType,2>));
            if (!mem) throw std::bad_alloc{};
            auto* p = new (mem) Array<NumType,2>(inputs->shape); 
            layer.saved_inputs = p;


            void* memout = std::malloc(sizeof(Array<NumType,2>));
            if (!memout) throw std::bad_alloc{};
            auto* pout = new (memout) Array<NumType,2>(inputs->shape); 
            layer.outputs = pout;


            //Array<NumType, 2> outputs = Array<NumType, 2>(inputs->shape);
            for(size_t i = 0; i < inputs->shape[0]; i++){
                for(size_t j = 0; j < inputs->shape[1]; j++){
                    layer.saved_inputs->fastSet2D(i, j, inputs->fastGet2D(i, j));
                    if(inputs->fastGet2D(i, j) < layer.relmin){
                        layer.outputs->fastSet2D(i, j, layer.relmin);
                    }
                    else{
                        layer.outputs->fastSet2D(i,j, inputs->fastGet2D(i,j));
                    }
                }
            }
            return layer.outputs;
    }
    
    // ReLU 0 Minimum
    if(layer.type == 0x1){
            void* mem = std::malloc(sizeof(Array<NumType,2>));
            if (!mem) throw std::bad_alloc{};
            auto* p = new (mem) Array<NumType,2>(inputs->shape); 
            layer.saved_inputs = p;

            void* memout = std::malloc(sizeof(Array<NumType,2>));
            if (!memout) throw std::bad_alloc{};
            auto* pout = new (memout) Array<NumType,2>(inputs->shape); 
            layer.outputs = pout;

            //Array<NumType, 2> outputs = Array<NumType, 2>(inputs.shape);
            for(size_t i = 0; i < inputs->shape[0]; i++){
                for(size_t j = 0; j < inputs->shape[1]; j++){
                    layer.saved_inputs->fastSet2D(i, j, inputs->fastGet2D(i, j));
                    if(inputs->fastGet2D(i, j) < 0){
                        layer.outputs->fastSet2D(i, j, 0);
                    }
                    else{
                        layer.outputs->fastSet2D(i,j, inputs->fastGet2D(i,j));
                    }
                }
            }
            return layer.outputs;
    }
    
    // Softmax
    if(layer.type == 0x2){
            
            //saved_samples = inputs.shape[0];
            //saved_prev_layer = inputs.shape[1];
            if(inputs->shape[0] <= 0){
                return nullptr;
            }            
            void* mem = std::malloc(sizeof(Array<NumType,2>));
            if (!mem) throw std::bad_alloc{};
            auto* p = new (mem) Array<NumType,2>(inputs->shape); 
            layer.saved_inputs = p;

            void* memout = std::malloc(sizeof(Array<NumType,2>));
            if (!memout) throw std::bad_alloc{};
            auto* pout = new (memout) Array<NumType,2>(inputs->shape); 
            layer.outputs = pout;

            /*if(this->outputs != nullptr){
                clearMatrix(this->outputs, samples);
                this->outputs = nullptr;
            }*/
            //size_t outputsShape[2] = {saved_samples, saved_prev_layer};
            //Array<NumType, 2> outputs = Array<NumType, 2>(inputs.shape);
            for(int i = 0; i < inputs->shape[0]; i++){
                NumType sum = 0.0f;
                NumType max = inputs->fastGet2D(i, 0);
                for(int j = 1; j < inputs->shape[1]; j++){
                    if(max < inputs->fastGet2D(i, j)){
                        max = inputs->fastGet2D(i, j);
                    }
                }
                for(int j = 0; j < inputs->shape[1]; j++){
                    layer.outputs->fastSet2D(i, j, exp(inputs->fastGet2D(i, j)-max));
                    sum += layer.outputs->fastGet2D(i, j);
                }
                for(int j = 0; j < inputs->shape[1]; j++){
                    
                    layer.outputs->fastSet2D(i, j, layer.outputs->fastGet2D(i,j)/(sum+1e-7));
                    layer.saved_inputs->fastSet2D(i, j, layer.outputs->fastGet2D(i,j));
                }
            }
            return layer.outputs;

    }
   
    // Leaky ReLU
    if(layer.type == 0x3){
        
        //saved_samples = inputs.shape[0];
        //saved_prev_layer = inputs.shape[1];
        if(inputs->shape[0] <= 0){
            return nullptr;
        }
        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(inputs->shape); 
        layer.saved_inputs = p;

        void* memout = std::malloc(sizeof(Array<NumType,2>));
        if (!memout) throw std::bad_alloc{};
        auto* pout = new (memout) Array<NumType,2>(inputs->shape); 
        layer.outputs = pout;

        //saved_samples = samples;
        //saved_prev_layer = prev_layer;
        //size_t savedShape[2] = {samples, prev_layer};
        //saved_inputs = Array<NumType, 2>(savedShape);
        //this->outputs = Array<NumType, 2>(savedShape);
        for(size_t i = 0; i < inputs->shape[0]; i++){
            for(size_t j = 0; j < inputs->shape[1]; j++){
                layer.saved_inputs->fastSet2D(i, j, inputs->fastGet2D(i, j));
                if(inputs->fastGet2D(i, j) < layer.relmin){
                    layer.outputs->fastSet2D(i, j, (inputs->fastGet2D(i, j) - layer.relmin)*layer.alpha+layer.relmin);
                }
                else{
                    layer.outputs->fastSet2D(i, j, inputs->fastGet2D(i, j));
                }
            }
        }
        //matrixViewer(saved_inputs, samples, prev_layer);
        return layer.outputs;

    }

    // Copied Linear
    if(layer.type == 0x4){
        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(inputs->shape); 
        layer.saved_inputs = p;

        void* memout = std::malloc(sizeof(Array<NumType,2>));
        if (!memout) throw std::bad_alloc{};
        auto* pout = new (memout) Array<NumType,2>(inputs->shape); 
        layer.outputs = pout;

        for(size_t i = 0; i < inputs->shape[0]; i ++){
            for(size_t j = 0; j < inputs->shape[1]; j++){
                layer.outputs->fastSet2D(i, j, inputs->fastGet2D(i, j));
                layer.saved_inputs->fastSet2D(i, j, inputs->fastGet2D(i, j));
            }
        }
        return layer.outputs;
    }
    
    // Flow Linear
    if(layer.type == 0x5){
        return inputs;
    }
    
    // Sigmoid
    if(layer.type == 0x6){

        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(inputs->shape); 
        layer.saved_inputs = p;

        void* memout = std::malloc(sizeof(Array<NumType,2>));
        if (!memout) throw std::bad_alloc{};
        auto* pout = new (memout) Array<NumType,2>(inputs->shape); 
        layer.outputs = pout;

        for(int i = 0; i < inputs->shape[0]; i++){
            for(int j = 0; j < inputs->shape[1]; j++){
                layer.outputs->fastSet2D(i, j, 1/(1+exp(-inputs->fastGet2D(i, j))));
                layer.saved_inputs->fastSet2D(i, j, layer.outputs->fastGet2D(i, j));
            }
        }

        return layer.outputs;
    }
    
    // Step
    if(layer.type == 0x7){
        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(inputs->shape); 
        layer.saved_inputs = p;

        void* memout = std::malloc(sizeof(Array<NumType,2>));
        if (!memout) throw std::bad_alloc{};
        auto* pout = new (memout) Array<NumType,2>(inputs->shape); 
        layer.outputs = pout;



        for(int i = 0; i < inputs->shape[0]; i++){
            for(int j = 0; j < inputs->shape[1]; j++){
                if(inputs->fastGet2D(i, j) < layer.relmin){
                    layer.outputs->fastSet2D(i, j, layer.alpha);
                }
                else{
                    layer.outputs->fastSet2D(i, j, layer.beta);
                }
            }
        }
        return layer.outputs;

    }

    // Single Alpha PReLU
    if(layer.type == 0x8){
        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(inputs->shape); 
        layer.saved_inputs = p;

        void* memout = std::malloc(sizeof(Array<NumType,2>));
        if (!memout) throw std::bad_alloc{};
        auto* pout = new (memout) Array<NumType,2>(inputs->shape); 
        layer.outputs = pout;

        for(int i = 0; i < inputs->shape[0]; i++){
            for(int j = 0; j < inputs->shape[1]; j++){
                layer.saved_inputs->fastSet2D(i, j, inputs->fastGet2D(i, j));
                if(inputs->fastGet2D(i, j) < layer.relmin){
                    layer.outputs->fastSet2D(i, j, (inputs->fastGet2D(i, j)-layer.relmin)*layer.alpha+layer.relmin);
                }
                else{
                    layer.outputs->fastSet2D(i, j, inputs->fastGet2D(i, j));
                }
            }
        }
        return layer.outputs;
    }

    // Array Length Alpha PReLU
    if(layer.type == 0x9){
        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(inputs->shape); 
        layer.saved_inputs = p;

        void* memout = std::malloc(sizeof(Array<NumType,2>));
        if (!memout) throw std::bad_alloc{};
        auto* pout = new (memout) Array<NumType,2>(inputs->shape); 
        layer.outputs = pout;


    }

    // Slope Linear
    if(layer.type == 0xa){
        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(inputs->shape); 
        layer.saved_inputs = p;

        void* memout = std::malloc(sizeof(Array<NumType,2>));
        if (!memout) throw std::bad_alloc{};
        auto* pout = new (memout) Array<NumType,2>(inputs->shape); 
        layer.outputs = pout;

        for(size_t i = 0; i < inputs->shape[0]; i ++){
            for(size_t j = 0; j < inputs->shape[1]; j++){
                layer.outputs->fastSet2D(i, j, inputs->fastGet2D(i, j)*layer.alpha);
                layer.saved_inputs->fastSet2D(i, j, inputs->fastGet2D(i, j));
            }
        }
        return layer.outputs;
    }
    
    if(layer.type == 0xb){
        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(inputs->shape); 
        layer.saved_inputs = p;

        void* memout = std::malloc(sizeof(Array<NumType,2>));
        if (!memout) throw std::bad_alloc{};
        auto* pout = new (memout) Array<NumType,2>(inputs->shape); 
        layer.outputs = pout;

        for(size_t i = 0; i < inputs->shape[0]; i ++){
            for(size_t j = 0; j < inputs->shape[1]; j++){
                layer.outputs->fastSet2D(i, j, inputs->fastGet2D(i, j)*layer.alpha+layer.beta);
                layer.saved_inputs->fastSet2D(i, j, inputs->fastGet2D(i, j));
            }
        }
        return layer.outputs;
    }

    // Reverse ReLU
    if(layer.type == 0xc){
        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(inputs->shape); 
        layer.saved_inputs = p;


        void* memout = std::malloc(sizeof(Array<NumType,2>));
        if (!memout) throw std::bad_alloc{};
        auto* pout = new (memout) Array<NumType,2>(inputs->shape); 
        layer.outputs = pout;


        for(size_t i = 0; i < inputs->shape[0]; i++){
            for(size_t j = 0; j < inputs->shape[1]; j++){
                layer.saved_inputs->fastSet2D(i, j, inputs->fastGet2D(i, j));
                if(inputs->fastGet2D(i, j) > layer.relmin){
                    layer.outputs->fastSet2D(i, j, layer.relmin);
                }
                else{
                    layer.outputs->fastSet2D(i, j, inputs->fastGet2D(i,j));
                }
            }
        }
        return layer.outputs;
    }


    return nullptr;
}


template <typename NumType>
Array<NumType, 2>* activationBackward(Array<NumType, 2>* dvalues, ActivationLayer<NumType>& layer){
    
    // ReLU Arbitrary Minimum
    if(layer.type == 0x0){

        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(layer.saved_inputs->shape); 

        layer.dinputs = p;


        for(size_t i = 0; i < layer.saved_inputs->shape[0]; i++){
            for(size_t j = 0; j < layer.saved_inputs->shape[1]; j++){
                if(layer.saved_inputs->fastGet2D(i, j) <= layer.relmin){
                    layer.dinputs->fastSet2D(i, j, 0);
                }
                else{
                    layer.dinputs->fastSet2D(i, j, dvalues->fastGet2D(i,j));
                }
            }
        }
        return layer.dinputs;
    }
    
    // ReLU 0 Minimum
    if(layer.type == 0x1){

        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(layer.saved_inputs->shape); 

        layer.dinputs = p;


        for(size_t i = 0; i < layer.saved_inputs->shape[0]; i++){
            for(size_t j = 0; j < layer.saved_inputs->shape[1]; j++){
                if(layer.saved_inputs->fastGet2D(i, j) <= 0){
                    layer.dinputs->fastSet2D(i, j, 0);
                }
                else{
                    layer.dinputs->fastSet2D(i, j, dvalues->fastGet2D(i,j));
                }
            }
        }
        return layer.dinputs;
    }

    // Softmax   
    if(layer.type == 0x2){
        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(layer.saved_inputs->shape); 

        layer.dinputs = p;        

        for(int i = 0; i < layer.saved_inputs->shape[0]; i++){

            for(int j = 0; j < layer.saved_inputs->shape[1]; j++) {
                layer.dinputs->fastSet2D(i, j, 0.0f);
                for(int k = 0; k < layer.saved_inputs->shape[1]; k++) {
                    if (k == j) {
                        layer.dinputs->fastInc2D(i, j, (layer.saved_inputs->fastGet2D(i, j) * (1 - layer.saved_inputs->fastGet2D(i, j))) * dvalues->fastGet2D(i, k));
                    } else {
                        layer.dinputs->fastInc2D(i, j, (-layer.saved_inputs->fastGet2D(i, j) * layer.saved_inputs->fastGet2D(i, k)) * dvalues->fastGet2D(i, k));  
                    }
                }
            }
        }

        return layer.dinputs;
    }
    
    // Leaky ReLU
    if(layer.type == 0x3){
        //size_t dinputsShape[2] = {saved_samples, saved_prev_layer};
        //this->dinputs = Array<NumType, 2>(dinputsShape);

        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(layer.saved_inputs->shape); 

        layer.dinputs = p;


        for(size_t i = 0; i < layer.saved_inputs->shape[0]; i++){
            for(size_t j = 0; j < layer.saved_inputs->shape[1]; j++){
                if(layer.saved_inputs->fastGet2D(i, j) <= layer.relmin){
                    layer.dinputs->fastSet2D(i, j, dvalues->fastGet2D(i, j)*layer.alpha);
                }
                else{
                    layer.dinputs->fastSet2D(i, j, dvalues->fastGet2D(i, j));
                }
            }
        }
        return layer.dinputs;
    }
    
    // Copied Linear
    if(layer.type == 0x4){
        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(layer.saved_inputs->shape); 

        layer.dinputs = p;

        for(size_t i = 0; i < layer.saved_inputs->shape[0]; i++){
            for(size_t j = 0; j < layer.saved_inputs->shape[1]; j++){
                layer.dinputs->fastSet2D(i, j, dvalues->fastGet2D(i, j));
            }
        }
        return layer.dinputs;
    }
    
    // Flow Linear
    if(layer.type == 0x5){
        return dvalues;
    }
    
    // Sigmoid
    if(layer.type == 0x6){
        //size_t dinputsShape[2] = {saved_samples, saved_prev_layer};
        //this->dinputs = Array<NumType, 2>(dinputsShape);

        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(layer.saved_inputs->shape); 

        layer.dinputs = p;


        for(int i = 0; i < layer.saved_inputs->shape[0]; i++){
            for(int j = 0; j < layer.saved_inputs->shape[1]; j++){
                layer.dinputs->fastSet2D(i, j, layer.saved_inputs->fastGet2D(i,j )*(1-layer.saved_inputs->fastGet2D(i, j))*dvalues->fastGet2D(i, j));
            }
        }
        return layer.dinputs;
    }
    
    // Step
    if(layer.type == 0x7){
        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(layer.saved_inputs->shape); 

        layer.dinputs = p;

        for(int i = 0; i < layer.saved_inputs->shape[0]; i++){
            for(int j = 0; j < layer.saved_inputs->shape[1]; j++){
                // OH IF x=relmin DERIVATIVE IS UNDEFINED IN STEP???? REALLY???? OK. THEN BY SOME CANCELLATION STUFF THERE IS NO WAY TO KNOW IF X AND THE OTHER THING ARE ACTUALLY EQUAL BY SOME FLOATING POINT APPROXIMATION OF 2 VALUES SO PLEASE LEAVE ME ALONE.
                layer.dinputs->fastSet2D(i, j, 0);
            }
        }
        return layer.dinputs;

    }

    // Single Alpha PReLU
    if(layer.type == 0x8){
        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(layer.saved_inputs->shape); 

        layer.dinputs = p;

        layer.beta = 0.0f;
        for(int i = 0; i < layer.saved_inputs->shape[0]; i++){
            for(int j = 0; j < layer.saved_inputs->shape[1]; j++){
                if(layer.saved_inputs->fastGet2D(i, j) < layer.relmin){
                    layer.dinputs->fastSet2D(i, j, dvalues->fastGet2D(i, j)*layer.alpha);
                    layer.beta += dvalues->fastGet2D(i, j)*(layer.saved_inputs->fastGet2D(i, j)-layer.relmin);
                }
                else{
                    layer.dinputs->fastSet2D(i, j, dvalues->fastGet2D(i,j));
                }
            }
        }
        return layer.dinputs;
    }

    // Array Length Alpha PReLU
    if(layer.type == 0x9){
        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(layer.saved_inputs->shape); 

        layer.dinputs = p;

    }

    // Slope Linear and Slope Linear Offset (because y=mx+b dy/dx = m regardless of b == 0 || b != 0 (or I'm just bad at calc and wrote a bug))
    if(layer.type == 0xa || layer.type == 0xb){
        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(layer.saved_inputs->shape); 

        layer.dinputs = p;

        for(size_t i = 0; i < layer.saved_inputs->shape[0]; i++){
            for(size_t j = 0; j < layer.saved_inputs->shape[1]; j++){
                layer.dinputs->fastSet2D(i, j, dvalues->fastGet2D(i, j)*layer.alpha);
            }
        }
        return layer.dinputs;
    }

    // Reverse ReLU
    if(layer.type == 0xc){

        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(layer.saved_inputs->shape); 

        layer.dinputs = p;


        for(size_t i = 0; i < layer.saved_inputs->shape[0]; i++){
            for(size_t j = 0; j < layer.saved_inputs->shape[1]; j++){
                if(layer.saved_inputs->fastGet2D(i, j) >= layer.relmin){
                    layer.dinputs->fastSet2D(i, j, 0);
                }
                else{
                    layer.dinputs->fastSet2D(i, j, dvalues->fastGet2D(i,j));
                }
            }
        }
        return layer.dinputs;
    }

    return nullptr;
}


// Clears Logits
template <typename NumType>
void freeActivationLogits(ActivationLayer<NumType>& layer){
    // Force to be false in Python
    if(layer.outputOwnership){
        delete layer.outputs;
    }

    delete layer.saved_inputs;
    delete layer.dinputs;
}

// Update Tuneable Params
template <typename NumType>
void updateParams(ActivationLayer<NumType>& layer){
    
}



#include "arbitraryactivation.tpp"
#endif

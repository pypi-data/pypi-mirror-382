#ifndef ArbitraryActivation_HPP
#define ArbitraryActivation_HPP

#include "../../matrix/matrix.hpp"
#include <cstdint>


template <typename NumType = float>
struct ActivationLayer {
    /*
     * Types:
     * 0x0: ReLU w/ any arbitrary minimum, uses field relmin
     * 0x1: ReLU w/ 0 as a forced minimum, uses a hardcoded 0 constant to avoid memory
     * 0x2: Softmax
     * 0x3: Leaky ReLU
     * 0x4: Copied Linear (Linear with logits stored. Strongly discourged)
     * 0x5: Flow Linear (Linear without logits stored. Better but still useless)
     * 0x6: Sigmoid
     * 0x7: Step
     * 0x8: Single Parameter PReLU
     * 0x9: Array of Parameter Alpha's PReLU
     * 0xa: Slope Linear
     * 0xb: y=mx+b Linear
     * 0xc: Reverse ReLU
     */
    uint8_t type;
    Array<NumType,2>* saved_inputs;
    Array<NumType,2>* dinputs;

    // Minimum for relu leaky relu, bar between 0 and 1 for step
    NumType relmin;

    // Combine these to determine what gets sent upwards
    Array<NumType, 2>* outputs;
    bool outputOwnership;

    // Used in Leaky ReLU as leaking param, using in step as the MINIMUM, Slope in slope linears
    NumType alpha;

    // Used in step as the maximum, derivative of alpha in PReLU, offset in slope + beta linears
    NumType beta;
};


template <typename NumType = float>
Array<NumType, 2>* activationForward(Array<NumType, 2>* inputs, ActivationLayer<NumType>& layer);

template <typename NumType = float>
Array<NumType, 2>* activationBackward(Array<NumType, 2>* dvalues, ActivationLayer<NumType>& layer);


// Warning after a call all logits and anything malloced with the address in the layer struct disappear permanently
template <typename NumType = float>
void freeActivationLogits(ActivationLayer<NumType>& layer);

// Update Tuneable Params
template <typename NumType = float>
void updateParams(ActivationLayer<NumType>& layer);

#include "arbitraryactivation.tpp"
#endif

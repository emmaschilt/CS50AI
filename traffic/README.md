I initially tested my model architecture with:
- 1 Convolutional Layer, CONV2D, 32 filters, 3x3 kernels, ReLU activation
- 1 Pooling layer, MaxPooling2D, 2x2
- 1 Flattening layer 
- 1 Hidden Dense layer, 64 neurons, ReLU
- 1 Output Layer, softmax activation
- With adam optimiser, categorical crossentropy loss
* Resulting in very poor performance (loss: 3.4944 - accuracy: 0.0544 - 516ms/epoch - 2ms/step)

- Early improvements experimenting with an additional convolutional (64 filters) and pooling layer
* Resulting in a substantial improvement (loss: 0.3187 - accuracy: 0.9107 - 920ms/epoch - 3ms/step)

- I tried an additional convolutional and pooling layer again, and found a drop in accuracy (0.88), so I removed them

- Tested an additional dense layer and changed the loss function to binary crossentrophy 
* Another substantial improvement (loss: 0.0065 - accuracy: 0.9766 - 851ms/epoch - 3ms/step)

- For the final optimisation I increased the first dense layer to 128 neurons to reach an impressive 97.8% accuracy
* loss: 0.0077 - accuracy: 0.9781 - 845ms/epoch - 3ms/step


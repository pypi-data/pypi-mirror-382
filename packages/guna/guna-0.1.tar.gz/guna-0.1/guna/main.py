def q1():
    print("""import tensorflow as tf
import numpy as np
from PIL import Image
from tkinter import filedialog, Tk
import matplotlib.pyplot as plt

# Load and preprocess MNIST
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
x_train = x_train[..., tf.newaxis] / 255.0
x_test = x_test[..., tf.newaxis] / 255.0
y_train = tf.one_hot(y_train, 10)
y_test = tf.one_hot(y_test, 10)

# Initialize weights
W1 = tf.Variable(tf.random.normal([3, 3, 1, 32]))
B1 = tf.Variable(tf.zeros([32]))
W2 = tf.Variable(tf.random.normal([3, 3, 32, 64]))
B2 = tf.Variable(tf.zeros([64]))
W3 = tf.Variable(tf.random.normal([3, 3, 64, 64]))
B3 = tf.Variable(tf.zeros([64]))
W_fc1 = tf.Variable(tf.random.normal([7*7*64, 128]))
B_fc1 = tf.Variable(tf.zeros([128]))
W_fc2 = tf.Variable(tf.random.normal([128, 10]))
B_fc2 = tf.Variable(tf.zeros([10]))

# Model
def model(x):
    x = tf.nn.relu(tf.nn.conv2d(x, W1, 1, 'SAME') + B1)
    x = tf.nn.max_pool2d(x, 2, 2, 'SAME')
    x = tf.nn.relu(tf.nn.conv2d(x, W2, 1, 'SAME') + B2)
    x = tf.nn.max_pool2d(x, 2, 2, 'SAME')
    x = tf.nn.relu(tf.nn.conv2d(x, W3, 1, 'SAME') + B3)
    x = tf.reshape(x, [-1, 7*7*64])
    x = tf.nn.relu(tf.matmul(x, W_fc1) + B_fc1)
    return tf.matmul(x, W_fc2) + B_fc2

optimizer = tf.optimizers.Adam()
batch_size = 64

# Training loop
for epoch in range(3):
    for i in range(0, len(x_train), batch_size):
        x_batch = x_train[i:i+batch_size]
        y_batch = y_train[i:i+batch_size]
        with tf.GradientTape() as tape:
            logits = model(x_batch)
            loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=y_batch))
        grads = tape.gradient(loss, [W1,W2,W3,W_fc1,W_fc2,B1,B2,B3,B_fc1,B_fc2])
        optimizer.apply_gradients(zip(grads, [W1,W2,W3,W_fc1,W_fc2,B1,B2,B3,B_fc1,B_fc2]))
    print(f"Epoch {epoch+1} done")

# Accuracy
pred = tf.argmax(model(x_test), axis=1)
true = tf.argmax(y_test, axis=1)
acc = tf.reduce_mean(tf.cast(tf.equal(pred, true), tf.float32))
print(f"Test Accuracy: {acc.numpy():.4f}")

# Predict image from test
image_index = int(input("Enter the index of the image to predict (0-9999): "))
img = x_test[image_index]
img_reshaped = img.reshape(1, 28, 28, 1)
prediction = model(img_reshaped)
predicted_class = np.argmax(prediction)
plt.imshow(img.reshape(28, 28), cmap='gray')
plt.title(f'Predicted class: {predicted_class}')
plt.axis('off')
plt.show()""")

def q2():
    print("""import numpy as np
from tensorflow.keras.models import load_model
from tensorflow import keras
from tensorflow.keras.datasets import mnist
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.layers import Conv2D, MaxPooling2D
from tensorflow.keras import backend as K
(x_train, y_train), (x_test, y_test) = mnist.load_data()
print(x_train.shape, y_train.shape)
x_train = x_train.reshape(x_train.shape[0], 28, 28, 1)
x_test = x_test.reshape(x_test.shape[0], 28, 28, 1)
input_shape = (28, 28, 1)
y_train = keras.utils.to_categorical(y_train, 10)
y_test = keras.utils.to_categorical(y_test, 10)
x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
x_train /= 255
x_test /= 255
print('x_train shape:', x_train.shape)
print(x_train.shape[0], 'train samples')
print(x_test.shape[0], 'test samples')
batch_size = 128
num_classes = 10
epochs = 1
model = Sequential()
model.add(Conv2D(32, kernel_size=(5, 5), activation='relu', input_shape=input_shape))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.3))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(num_classes, activation='softmax'))
model.compile(loss=keras.losses.categorical_crossentropy,
              optimizer=keras.optimizers.Adadelta(),
              metrics=['accuracy'])
hist = model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, verbose=1, validation_data=(x_test, y_test))
print("The model has successfully trained")
score = model.evaluate(x_test, y_test, verbose=0)
print('Test loss:', score[0])
print('Test accuracy:', score[1])
image_index = int(input("Enter the index of the image to predict (0-9999): "))
img = x_test[image_index]
img_reshaped = img.reshape(1, 28, 28, 1)
prediction = model.predict(img_reshaped)
predicted_class = np.argmax(prediction)
!pip install matplotlib
import matplotlib.pyplot as plt
plt.imshow(img.reshape(28, 28), cmap='gray')
plt.title(f'Predicted class: {predicted_class}')
plt.axis('off')
plt.show()""")

def q3():
    print("""import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, Input, Model
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import CategoricalCrossentropy
from tensorflow.keras.callbacks import ReduceLROnPlateau, EarlyStopping
train_dir = "/kaggle/input/cars-image-dataset/Cars Dataset/train"
test_dir =  "/kaggle/input/cars-image-dataset/Cars Dataset/test"
import os


if not os.path.exists(train_dir):
    print(f"Error: Training directory not found at {train_dir}")
    # Try listing the parent directory to see available contents
    parent_dir = os.path.dirname(train_dir)
    if os.path.exists(parent_dir):
        print(f"Contents of parent directory {parent_dir}:")
        !ls {parent_dir}
    else:
        print(f"Parent directory {parent_dir} also not found.")
else:
    print(f"Training directory found at {train_dir}")

if not os.path.exists(test_dir):
    print(f"Error: Test directory not found at {test_dir}")
    parent_dir = os.path.dirname(test_dir)
    if os.path.exists(parent_dir):
        print(f"Contents of parent directory {parent_dir}:")
        !ls {parent_dir}
    else:
         print(f"Parent directory {parent_dir} also not found.")
else:
    print(f"Test directory found at {test_dir}")



batch_size = 32
img_width, img_height = 128, 128
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=10,
    horizontal_flip=True,
    zoom_range=0.2,
    width_shift_range=0.2,
    height_shift_range=0.2
)
train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode="sparse",
    shuffle=True
)
test_datagen = ImageDataGenerator(
    rescale=1./255
)
test_generator = test_datagen.flow_from_directory(
    test_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode="sparse",
    shuffle=False
)
print("Classes found in training set: ", train_generator.class_indices)
print("Classes found in test set: ", test_generator.class_indices)

batch_size = 32
img_width, img_height = 128, 128
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=10,
    horizontal_flip=True,
    zoom_range=0.2,
    width_shift_range=0.2,
    height_shift_range=0.2
)
train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode="sparse",
    shuffle=True
)

def AlexNet():
    inp = layers.Input((img_width, img_height, 3))
    x = layers.Conv2D(96, kernel_size=11, strides=4, activation='relu')(inp)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D(pool_size=3, strides=2)(x)
    x = layers.Conv2D(256, kernel_size=5, padding='same', activation='relu')(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D(pool_size=3, strides=2)(x)
    x = layers.Conv2D(384, kernel_size=3, padding='same', activation='relu')(x)
    x = layers.Conv2D(384, kernel_size=3, padding='same', activation='relu')(x)
    x = layers.Conv2D(256, kernel_size=3, padding='same', activation='relu')(x)
    x = layers.MaxPooling2D(pool_size=3, strides=2)(x)
    x = layers.Flatten()(x)
    x = layers.Dense(4096, activation='relu')(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(4096, activation='relu')(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(7, activation='softmax')(x)

    model_Alex = models.Model(inputs=inp, outputs=x)

    return model_Alex

model_Alex = AlexNet()
model_Alex.summary()

tf.keras.utils.plot_model(
    model_Alex,
    to_file='alex_model.png',
    show_shapes=True,
    show_dtype=False,
    show_layer_names=True,
    show_layer_activations=True,
    dpi=100
)

model_Alex.compile(
    optimizer=Adam(learning_rate=1e-4),
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
    metrics=['accuracy']
)

reduce_lr = ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.2,
    patience=5,
    min_lr=1e-6,
    verbose=1
)

early_stopping = EarlyStopping(
    monitor='val_loss',
    patience=10,
    restore_best_weights=True,
    verbose=1
)

Alex_model = model_Alex.fit(train_generator,
    validation_data=test_generator,
    epochs=1,
    callbacks=[reduce_lr,early_stopping]
)

training_loss_alex = Alex_model.history['loss']
val_loss_alex = Alex_model.history['val_loss']
training_acc_alex = Alex_model.history['accuracy']
val_acc_alex = Alex_model.history['val_accuracy']

plt.figure(figsize=(14, 5))

plt.subplot(1, 2, 1)
plt.plot(training_loss_alex, label='Training Loss')
plt.plot(val_loss_alex, label='Validation Loss')
plt.title('Loss during training and validation')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(training_acc_alex, label='Training Accuracy')
plt.plot(val_acc_alex, label='Validation Accuracy')
plt.title('Accuracy during training and validation')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()

plt.show()""")

def q4():
    print("""
!pip install -q tensorflow pillow matplotlib numpy
import os
import random
import math
import numpy as np
from PIL import Image, ImageDraw
import tensorflow as tf
from tensorflow.keras import layers, models, losses, optimizers
import matplotlib.pyplot as plt
def generate_image(size=128):
    bg_color=(random.randint(0,255),random.randint(0,255),random.randint(0,255))
    img=Image.new('RGB',(size,size),bg_color)
    draw=ImageDraw.Draw(img)
    obj_w=random.randint(size//8,size//3)
    obj_h=random.randint(size//8,size//3)
    x0=random.randint(0,size-obj_w-1)
    y0=random.randint(0,size-obj_h-1)
    x1=x0+obj_w
    y1=y0+obj_h
    cls=random.randint(0,1)
    if cls==0:
        fill=(255,0,0)
    else:
        fill=(0,255,0)
    draw.rectangle([x0,y0,x1,y1],fill=fill)
    img=np.array(img)/255.0
    bbox=np.array([x0/size,y0/size,x1/size,y1/size],dtype=np.float32)
    return img,cls,bbox
def create_dataset(n,size=128):
    imgs=[]
    clss=[]
    bboxes=[]
    for _ in range(n):
        img,cls,bbox=generate_image(size)
        imgs.append(img)
        clss.append(cls)
        bboxes.append(bbox)
    return np.array(imgs,dtype=np.float32),np.array(clss,dtype=np.int32),np.array(bboxes,dtype=np.float32)
x_train,y_train_cls,y_train_bbox=create_dataset(2000,128)
x_val,y_val_cls,y_val_bbox=create_dataset(300,128)
def build_model(input_shape=(128,128,3)):
    inp=layers.Input(shape=input_shape)
    x=layers.Conv2D(32,3,activation='relu')(inp)
    x=layers.MaxPool2D()(x)
    x=layers.Conv2D(64,3,activation='relu')(x)
    x=layers.MaxPool2D()(x)
    x=layers.Conv2D(128,3,activation='relu')(x)
    x=layers.MaxPool2D()(x)
    x=layers.Flatten()(x)
    x=layers.Dense(128,activation='relu')(x)
    cls_out=layers.Dense(2,activation='softmax',name='class')(x)
    bbox_out=layers.Dense(4,activation='sigmoid',name='bbox')(x)
    model=models.Model(inputs=inp,outputs=[cls_out,bbox_out])
    model.compile(optimizer=optimizers.Adam(1e-3),loss={'class':'sparse_categorical_crossentropy','bbox':'mse'},metrics={'class':'accuracy'})
    return model
model=build_model()
history=model.fit(x_train,{'class':y_train_cls,'bbox':y_train_bbox},validation_data=(x_val,{'class':y_val_cls,'bbox':y_val_bbox}),epochs=10,batch_size=32)
os.makedirs('outputs',exist_ok=True)
test_imgs,,=create_dataset(10,128)
preds=model.predict(test_imgs)
pred_classes=np.argmax(preds[0],axis=1)
pred_bboxes=preds[1]
def draw_box_on_image(img_arr,bbox,cls,save_path):
    size=img_arr.shape[0]
    img=(img_arr*255).astype(np.uint8)
    pil=Image.fromarray(img)
    draw=ImageDraw.Draw(pil)
    x0=int(bbox[0]*size)
    y0=int(bbox[1]*size)
    x1=int(bbox[2]*size)
    y1=int(bbox[3]*size)
    draw.rectangle([x0,y0,x1,y1],outline=(255,255,0),width=2)
    draw.text((5,5),str(int(cls)),fill=(255,255,255))
    pil.save(save_path)
for i in range(len(test_imgs)):
    savef=f"outputs/result_{i}.png"
    draw_box_on_image(test_imgs[i],pred_bboxes[i],pred_classes[i],savef)
    display(Image.open(savef))""")
def q5():
    print( """
!git clone https://github.com/WongKinYiu/yolov9.git
%cd yolov9
!wget  https://github.com/WongKinYiu/yolov9/releases/download/v0.1/yolov9-c-converted.pt
!python detect.py --source './data/images/horses.jpg' --img 640 \
  --device 0 --weights './yolov9-c-converted.pt' \
  --name yolov9_c_c_640_detect
import matplotlib.pyplot as plt
import cv2
img = cv2.imread('/content/yolov9/runs/detect/yolov9_c_c_640_detect/horses.jpg')
plt.figure(figsize=(20,30))
plt.imshow(img)
plt.xticks([])
plt.yticks([])
plt.show()
!python detect.py --source '/content/yolov9/data/images/Dog_Car-1.jpg' --img 640 \
  --device "cpu" --weights './yolov9-c-converted.pt' \
  --name yolov9_c_c_640_detect
img = cv2.imread('/content/yolov9/runs/detect/yolov9_c_c_640_detect2/Dog_Car-1.jpg')
plt.figure(figsize=(20,30))
plt.imshow(img)
plt.xticks([])
plt.yticks([])
plt.show()
!python detect.py --source '/content/yolov9/data/images/Dog_Cycle_Person.jpg' --img 640 \
  --device "cpu" --weights './yolov9-c-converted.pt' \
  --name yolov9_c_c_640_detect
img = cv2.imread('/content/yolov9/runs/detect/yolov9_c_c_640_detect3/Dog_Cycle_Person.jpg')
plt.figure(figsize=(20,30))
plt.imshow(img)
plt.xticks([])
plt.yticks([])
plt.show()



""")
def q6():
    print("""
!pip install torch torchvision pillow tqdm lmdb

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision.utils import save_image, make_grid
from torchvision import transforms, datasets
import matplotlib.pyplot as plt
class Generator(nn.Module):
    def _init_(self):
        super()._init_()
        self.down = nn.Sequential(
            nn.Conv2d(3, 64, 4, 2, 1), nn.ReLU(),
            nn.Conv2d(64, 128, 4, 2, 1), nn.ReLU()
        )
        self.up = nn.Sequential(
            nn.ConvTranspose2d(128, 64, 4, 2, 1), nn.ReLU(),
            nn.ConvTranspose2d(64, 3, 4, 2, 1), nn.Tanh()
        )

    def forward(self, x):
        return self.up(self.down(x))


class Discriminator(nn.Module):
    def _init_(self):
        super()._init_()
        self.model = nn.Sequential(
            nn.Conv2d(6, 64, 4, 2, 1), nn.LeakyReLU(0.2),
            nn.Conv2d(64, 1, 4, 2, 1), nn.Sigmoid()
        )

    def forward(self, a, b):
        return self.model(torch.cat([a, b], 1))

transform = transforms.Compose([
    transforms.Resize((64, 64)),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

dataset = datasets.CIFAR10(root='./data', download=True, train=True, transform=transform)
loader = torch.utils.data.DataLoader(dataset, batch_size=2, shuffle=True)

device = "cuda" if torch.cuda.is_available() else "cpu"
G, D = Generator().to(device), Discriminator().to(device)
criterion = nn.BCELoss()
opt_G = optim.Adam(G.parameters(), 0.0002, betas=(0.5, 0.999))
opt_D = optim.Adam(D.parameters(), 0.0002, betas=(0.5, 0.999))

for epoch in range(1):
    for i, (img, label) in enumerate(loader):
        real_A = img.to(device)
        real_B = img.to(device)

        # Generate fake
        fake_B = G(real_A)

        # --- Train Discriminator ---
        opt_D.zero_grad()
        d_real_output = D(real_A, real_B)
        loss_D_real = criterion(d_real_output, torch.ones_like(d_real_output))
        d_fake_output = D(real_A, fake_B.detach())
        loss_D_fake = criterion(d_fake_output, torch.zeros_like(d_fake_output))
        loss_D = (loss_D_real + loss_D_fake) / 2
        loss_D.backward()
        opt_D.step()

        # --- Train Generator ---
        opt_G.zero_grad()
        g_fake_output = D(real_A, fake_B)
        loss_G_GAN = criterion(g_fake_output, torch.ones_like(g_fake_output))
        loss_G_L1 = nn.L1Loss()(fake_B, real_B) * 100
        loss_G = loss_G_GAN + loss_G_L1
        loss_G.backward()
        opt_G.step()

        if i % 50 == 0:
            print(f"Epoch {epoch+1}, Step {i}: Loss_D={loss_D.item():.4f}, Loss_G={loss_G.item():.4f}")
            grid = make_grid(torch.cat([real_A[:1], fake_B[:1], real_B[:1]]), nrow=3, normalize=True, value_range=(-1, 1))
            save_image(grid, "sample.png")
            plt.imshow(grid.permute(1, 2, 0).cpu().numpy())
            plt.axis("off")
            plt.show()
            break

torch.save(G.state_dict(), "G.pth")
print("✅ Generator saved as G.pth")
G.eval()
test_A, _ = next(iter(loader))
test_A = test_A[:1].to(device)

with torch.no_grad():
    fake_out = G(test_A)

test_B = test_A.clone()
grid = make_grid(torch.cat([test_A, fake_out, test_B]), nrow=3, normalize=True, value_range=(-1, 1))
save_image(grid, "output.png")
print("✅ Saved translated output as output.png")

from IPython.display import Image, display
display(Image(filename="output.png")) """)

def q7():
    print("""import tensorflow as tf 
from tensorflow.keras.layers import Dense, Flatten, Reshape, LeakyReLU 
from tensorflow.keras.models import Sequential 
import numpy as np 
import matplotlib.pyplot as plt 
 
 
(x_train, y_train), (x_test,y_test) = tf.keras.datasets.mnist.load_data() 
x_train = x_train / 127.5 - 1.0  # Normalize to [-1, 1] 
print('Shape of training data:', x_train.shape) 
 
 
def build_generator(): 
    model = Sequential() 
    model.add(Dense(256, input_dim=100)) 
    model.add(LeakyReLU(alpha=0.2)) 
    model.add(Dense(512)) 
    model.add(LeakyReLU(alpha=0.2)) 
    model.add(Dense(1024)) 
    model.add(LeakyReLU(alpha=0.2)) 
    model.add(Dense(28*28, activation='tanh')) 
    model.add(Reshape((28,28))) 
    return model 
 
generator = build_generator() 
generator.summary() 
 
 
def build_discriminator(): 
    model = Sequential() 
    model.add(Flatten(input_shape=(28,28))) 
    model.add(Dense(512)) 
    model.add(LeakyReLU(alpha=0.2)) 
    model.add(Dense(256)) 
    model.add(LeakyReLU(alpha=0.2)) 
    model.add(Dense(1, activation='sigmoid')) 
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy']) 
    return model 
 
discriminator = build_discriminator() 
discriminator.summary() 
 
 
def build_gan(generator, discriminator): 
    discriminator.trainable = False 
    model = Sequential() 
    model.add(generator) 
    model.add(discriminator) 
    model.compile(loss='binary_crossentropy', optimizer='adam') 
    return model 
 
gan = build_gan(generator, discriminator) 
gan.summary() 
 
 
epochs = 1000 
batch_size = 64 
sample_interval = 200  # smaller interval for smoother display 
 
real = np.ones((batch_size, 1)) 
fake = np.zeros((batch_size, 1)) 
 
for epoch in range(1, epochs+1): 
    
    idx = np.random.randint(0, x_train.shape[0], batch_size) 
    imgs = x_train[idx] 
    noise = np.random.normal(0, 1, (batch_size, 100)) 
    gen_imgs = generator.predict(noise, verbose=0) 
 
    d_loss_real = discriminator.train_on_batch(imgs, real) 
    d_loss_fake = discriminator.train_on_batch(gen_imgs, fake) 
    d_loss = 0.5 * np.add(d_loss_real, d_loss_fake) 
 
    
    noise = np.random.normal(0, 1, (batch_size, 100)) 
    g_loss = gan.train_on_batch(noise, real) 
 
   
    if epoch % sample_interval == 0: 
        print(f"Epoch {epoch} | D Loss: {d_loss[0]:.4f}, D Acc: {d_loss[1]*100:.2f}% | G Loss: {g_loss:.4f}") 
 
        
        idx = np.random.randint(0, x_train.shape[0], 25) 
        real_imgs = x_train[idx] 
        real_imgs = 0.5 * real_imgs + 0.5  # rescale to [0,1] 
 
         
        noise = np.random.normal(0, 1, (25, 100)) 
        gen_imgs = generator.predict(noise, verbose=0) 
        gen_imgs = 0.5 * gen_imgs + 0.5 
 
         
        fig, axs = plt.subplots(5, 10, figsize=(15,7)) 
        cnt = 0 
        for i in range(5): 
            for j in range(10): 
                if j < 5: 
                    axs[i,j].imshow(real_imgs[cnt], cmap='gray') 
                    axs[i,j].set_title("Real", fontsize=8) 
                else: 
                    axs[i,j].imshow(gen_imgs[cnt], cmap='gray') 
                    axs[i,j].set_title("Fake", fontsize=8) 
                    cnt += 1 
                axs[i,j].axis('off') 
        plt.tight_layout() 
        plt.show()""")
def q8():
    print("""!pip install -q tensorflow opencv-python matplotlib numpy 
 
import tensorflow as tf 
import numpy as np 
import cv2 
import os 
import matplotlib.pyplot as plt 
from tensorflow.keras import layers, models 
 
def create_synthetic_video(path,label,size=(64,64),frames=20): 
    os.makedirs(path,exist_ok=True) 
    fourcc=cv2.VideoWriter_fourcc(*'mp4v') 
    out=cv2.VideoWriter(os.path.join(path,f"{label}.mp4"),fourcc,5.0,size) 
    for i in range(frames): 
        frame=np.zeros((size[1],size[0],3),dtype=np.uint8) 
        if label=='red': 
            cv2.circle(frame,(i*3%size[0],size[1]//2),10,(0,0,255),-1) 
        else: 
            cv2.rectangle(frame,(i*3%size[0],i*2%size[1]),(i*3%size[0]+10,i*2%size[1]+10),(0,255,0),-1) 
        out.write(frame) 
    out.release() 
 
os.makedirs('videos',exist_ok=True) 
create_synthetic_video('videos','red') 
create_synthetic_video('videos','green') 
 
def load_video(path,frames=20,size=(64,64)): 
    cap=cv2.VideoCapture(path) 
    arr=[] 
    for i in range(frames): 
        ret,frame=cap.read() 
        if not ret: 
            break 
        frame=cv2.resize(frame,size) 
        arr.append(frame/255.0) 
    cap.release() 
    arr=np.array(arr) 
    return arr 
 
videos=[] 
labels=[] 
for f in os.listdir('videos'): 
    path=os.path.join('videos',f) 
    v=load_video(path) 
    videos.append(v) 
    labels.append(0 if 'red' in f else 1) 
x=np.array(videos) 
y=np.array(labels) 
 
model=models.Sequential([ 
    layers.Conv3D(8,(3,3,3),activation='relu',input_shape=(x.shape[1],64,64,3)), 
    layers.MaxPool3D((2,2,2)), 
    layers.Conv3D(16,(3,3,3),activation='relu'), 
    layers.GlobalAveragePooling3D(), 
    layers.Dense(2,activation='softmax') 
]) 
model.compile(optimizer='adam',loss='sparse_categorical_crossentropy',metrics=['accuracy']) 
model.fit(x,y,epochs=5) 
 
pred=model.predict(x) 
for i in range(len(pred)): 
    label=np.argmax(pred[i]) 
    plt.imshow(x[i][0]) 
    plt.title('Predicted:'+('red' if label==0 else 'green')) 
    plt.show()""")
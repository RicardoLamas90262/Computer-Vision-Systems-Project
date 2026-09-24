# System Architecture

## System Architecture Diagram

```text
[Camera]
    ↓
[Picamera2 Capture]
    ↓
[Computer Vision Processing]
    ↓
[Decision Logic]
    ↓
[Output / Action]
```

The camera captures an image and sends it to the Raspberry Pi. The computer vision program processes the image and identifies the target. The decision logic determines what to do with the information, and the final result is displayed or recorded.

## FOV and Mounting Distance Calculation

### 1. Physical Size of Target

The target is approximately **20 cm wide**.

### 2. Camera FOV

The camera has an estimated FOV of **60°**.

### 3. Mounting Distance

Using:

**FOV = 2 arctan(d / 2f)**

Rearranging to find distance:

**Distance = d / (2 × tan(FOV / 2))**

Substituting:

**Distance = 20 / (2 × tan(60° / 2))**

**Distance = 20 / (2 × tan(30°))**

**Distance ≈ 17.3 cm**

A mounting distance of about **20 cm** would give the camera some extra space around the target and help keep it fully in frame.

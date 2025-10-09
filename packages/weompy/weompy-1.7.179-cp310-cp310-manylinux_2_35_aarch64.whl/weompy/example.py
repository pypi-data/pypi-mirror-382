import weompy
import numpy as np
from matplotlib import pyplot as plt

if __name__ == "__main__":
    core = weompy.CoreManager()
    # If you are using a different connection than UART, change it accordingly
    core.connectUartAuto()

    image = core.captureImage()
    print(image)
    image_data = np.array(image.getData(), dtype=np.uint16).reshape(image.getHeight(), image.getWidth())
    plt.imshow(image_data, cmap='gray')
    plt.show()

    image.save("test.wti")

    allProperties = core.getPropertyIds()
    for property in allProperties:
        try:
            value = core.getPropertyValue(property)
            print('{0:<50} {1:<80} {2:>}'.format(property, "Value OK", str(value)))
        except Exception as e:
            print('{0:<50} {1:<80}'.format(property, str(e)))

    core.setPropertyValue("IMAGE_FREEZE", True)

    core.setPropertyValue("IMAGE_FREEZE", False)

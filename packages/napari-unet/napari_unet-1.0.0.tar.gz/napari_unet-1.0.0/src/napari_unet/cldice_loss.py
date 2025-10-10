import tensorflow as tf
from napari_unet.soft_skeleton import soft_skel

def soft_clDice_loss(iter_ = 50):
    """[function to compute dice loss]

    Args:
        iter_ (int, optional): [skeletonization iteration]. Defaults to 50.
    """
    def loss(y_true, y_pred):
        """[function to compute dice loss]

        Args:
            y_true ([float32]): [ground truth image]
            y_pred ([float32]): [predicted image]

        Returns:
            [float32]: [loss value]
        """
        smooth = 1.
        skel_pred = soft_skel(y_pred, iter_)
        skel_true = soft_skel(y_true, iter_)
        pres = (tf.math.reduce_sum(tf.math.multiply(skel_pred, y_true)[:,1:,:,:,:])+smooth)/(tf.math.reduce_sum(skel_pred[:,1:,:,:,:])+smooth)    
        rec = (tf.math.reduce_sum(tf.math.multiply(skel_true, y_pred)[:,1:,:,:,:])+smooth)/(tf.math.reduce_sum(skel_true[:,1:,:,:,:])+smooth)    
        cl_dice = 1.- 2.0*(pres*rec)/(pres+rec)
        return cl_dice
    return loss


def soft_dice(y_true, y_pred):
    """[function to compute dice loss]

    Args:
        y_true ([float32]): [ground truth image]
        y_pred ([float32]): [predicted image]

    Returns:
        [float32]: [loss value]
    """
    smooth = 1
    intersection = tf.math.reduce_sum((y_true * y_pred)[:,1:,:,:,:])
    coeff = (2. *  intersection + smooth) / (tf.math.reduce_sum(y_true[:,1:,:,:,:]) + tf.math.reduce_sum(y_pred[:,1:,:,:,:]) + smooth)
    return (1. - coeff)


def soft_dice_cldice_loss(iters = 15, alpha=0.5):
    """[function to compute dice+cldice loss]

    Args:
        iters (int, optional): [skeletonization iteration]. Defaults to 15.
        alpha (float, optional): [weight for the cldice component]. Defaults to 0.5.
    """
    def loss(y_true, y_pred):
        """[summary]

        Args:
            y_true ([float32]): [ground truth image]
            y_pred ([float32]): [predicted image]

        Returns:
            [float32]: [loss value]
        """
        smooth = 1.
        skel_pred = soft_skel(y_pred, iters)
        skel_true = soft_skel(y_true, iters)
        pres = (tf.math.reduce_sum(tf.math.multiply(skel_pred, y_true)[:,1:,:,:,:])+smooth)/(tf.math.reduce_sum(skel_pred[:,1:,:,:,:])+smooth)    
        rec = (tf.math.reduce_sum(tf.math.multiply(skel_true, y_pred)[:,1:,:,:,:])+smooth)/(tf.math.reduce_sum(skel_true[:,1:,:,:,:])+smooth)    
        cl_dice = 1.- 2.0*(pres*rec)/(pres+rec)
        dice = soft_dice(y_true, y_pred)
        return (1.0-alpha)*dice+alpha*cl_dice
    return loss

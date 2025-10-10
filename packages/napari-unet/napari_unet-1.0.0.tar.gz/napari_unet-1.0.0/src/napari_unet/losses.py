import tensorflow as tf
from napari_unet.soft_skeleton import soft_skel
from keras.losses import binary_crossentropy

def get_bce_loss(settings):
    def bce_loss(y_true, y_pred):
        y_true = tf.cast(y_true, tf.float32)
        y_pred = tf.cast(y_pred, tf.float32)
        bce = binary_crossentropy(y_true, y_pred)
        return tf.reduce_mean(bce)
    return bce_loss

def get_focal_loss(settings):
    focal_gamma = settings.get("focal_gamma", 2.0)
    focal_alpha = settings.get("focal_alpha", 0.25)
    def focal_loss(y_true, y_pred):
        y_true = tf.cast(y_true, tf.float32)
        y_pred = tf.cast(y_pred, tf.float32)
        alpha_t = y_true * focal_alpha + (1 - y_true) * (1 - focal_alpha)
        p_t = y_true * y_pred + (1 - y_true) * (1 - y_pred)
        fl = - alpha_t * (1 - p_t) ** focal_gamma * tf.math.log(p_t + 1e-5)
        return tf.reduce_mean(fl)
    return focal_loss

def get_tversky_loss(settings):
    tversky_alpha = settings.get("tversky_alpha", 0.3)
    beta = 1.0 - tversky_alpha
    def tversky_loss(y_true, y_pred):
        y_true = tf.cast(y_true, tf.float32)
        y_pred = tf.cast(y_pred, tf.float32)
        true_pos = tf.reduce_sum(y_true * y_pred)
        false_neg = tf.reduce_sum(y_true * (1 - y_pred))
        false_pos = tf.reduce_sum((1 - y_true) * y_pred)
        return 1 - (true_pos + 1) / (true_pos + tversky_alpha * false_neg + beta * false_pos + 1)
    return tversky_loss

# Dice and BCE-Dice losses

def get_dice_loss(settings):
    def dice_loss(y_true, y_pred):
        y_true = tf.cast(y_true, tf.float32)
        y_pred = tf.cast(y_pred, tf.float32)
        intersection = tf.reduce_sum(y_true * y_pred)
        return 1 - (2. * intersection + 1) / (tf.reduce_sum(y_true) + tf.reduce_sum(y_pred) + 1)
    return dice_loss

def get_bce_dice_loss(settings):
    bce_loss = get_bce_loss(settings)
    dice_loss = get_dice_loss(settings)
    bce_coef = settings.get("bce_coef", 0.25)
    def bce_dice_loss(y_true, y_pred):
        bce = bce_loss(y_true, y_pred)
        dice = dice_loss(y_true, y_pred)
        return bce_coef * bce + (1.0 - bce_coef) * dice
    return bce_dice_loss

# clDice and BCE-clDice losses

def get_cl_dice_loss(settings):
    iters = settings.get("skeleton_iterations", 30)
    def cl_dice_loss(y_true, y_pred):
        smooth = 0.0#1.
        skel_pred = soft_skel(y_pred, iters)
        skel_true = soft_skel(y_true, iters)
        pres = (tf.math.reduce_sum(tf.math.multiply(skel_pred, y_true))+smooth)/(tf.math.reduce_sum(skel_pred)+smooth)    
        rec = (tf.math.reduce_sum(tf.math.multiply(skel_true, y_pred))+smooth)/(tf.math.reduce_sum(skel_true)+smooth)    
        cl_dice = 1.- 2.0*(pres*rec)/(pres+rec)
        return cl_dice
    return cl_dice_loss

def get_bce_cl_dice_loss(settings):
    iters = settings.get("skeleton_iterations", 30)
    alpha = settings.get("cldice_alpha", 0.75)
    bce_loss = get_bce_loss(settings)
    def bce_cl_dice_loss(y_true, y_pred):
        smooth = 0.0
        skel_pred = soft_skel(y_pred, iters)
        skel_true = soft_skel(y_true, iters)
        pres = (tf.math.reduce_sum(tf.math.multiply(skel_pred, y_true))+smooth)/(tf.math.reduce_sum(skel_pred)+smooth)    
        rec = (tf.math.reduce_sum(tf.math.multiply(skel_true, y_pred))+smooth)/(tf.math.reduce_sum(skel_true)+smooth)    
        cl_dice = 1.- 2.0*(pres*rec)/(pres+rec)
        bce = bce_loss(y_true, y_pred)
        return (1.0-alpha)*bce+alpha*cl_dice
    return bce_cl_dice_loss

# Tversky and clDice loss
def get_tversky_cl_dice_loss(settings):
    iters = settings.get("skeleton_iterations", 30)
    lambda_tversky = settings.get("lambda_tversky", 0.5)
    tversky_loss = get_tversky_loss(settings)
    def tversky_cl_dice_loss(y_true, y_pred):
        smooth = 0.0
        skel_pred = soft_skel(y_pred, iters)
        skel_true = soft_skel(y_true, iters)
        pres = (tf.math.reduce_sum(tf.math.multiply(skel_pred, y_true))+smooth)/(tf.math.reduce_sum(skel_pred)+smooth)    
        rec = (tf.math.reduce_sum(tf.math.multiply(skel_true, y_pred))+smooth)/(tf.math.reduce_sum(skel_true)+smooth)    
        cl_dice = 1.- 2.0*(pres*rec)/(pres+rec)
        tversky = tversky_loss(y_true, y_pred)
        return lambda_tversky * tversky  + (1.0 - lambda_tversky) * cl_dice
    return tversky_cl_dice_loss
function Decoder(bytes, port) {
    // Decode an uplink message from a buffer
    // (array) of bytes to an object of fields.
    var decoded = {};

    // CPM
    var cpm = (bytes[1] << 8) + bytes[0];
    if (cpm > 0) decoded.cpm = cpm;

    // uSv/hr
    raw_usv_h = bytes[2] + bytes[3] * 256;
    var usv_h = sflt162f(raw_usv_h) * 10.0;
    if (usv_h > 0) decoded.usv_h = usv_h;

    // Mode
    var mode = (bytes[5] << 8) + bytes[4];
    if ([1, 2, 3, 4].indexOf(mode) > -1) decoded.mode = mode;

    return decoded;
}

function sflt162f(rawSflt16) {
    // rawSflt16 is the 2-byte number decoded from wherever;
    // it's in range 0..0xFFFF
    // bit 15 is the sign bit
    // bits 14..11 are the exponent
    // bits 10..0 are the the mantissa. Unlike IEEE format,
    // 	the msb is transmitted; this means that numbers
    //	might not be normalized, but makes coding for
    //	underflow easier.
    // As with IEEE format, negative zero is possible, so
    // we special-case that in hopes that JavaScript will
    // also cooperate.
    //
    // The result is a number in the open interval (-1.0, 1.0);
    //

    // throw away high bits for repeatability.
    rawSflt16 &= 0xFFFF;

    // special case minus zero:
    if (rawSflt16 == 0x8000)
        return -0.0;

    // extract the sign.
    var sSign = ((rawSflt16 & 0x8000) !== 0) ? -1 : 1;

    // extract the exponent
    var exp1 = (rawSflt16 >> 11) & 0xF;

    // extract the "mantissa" (the fractional part)
    var mant1 = (rawSflt16 & 0x7FF) / 2048.0;

    // convert back to a floating point number. We hope
    // that Math.pow(2, k) is handled efficiently by
    // the JS interpreter! If this is time critical code,
    // you can replace by a suitable shift and divide.
    var f_unscaled = sSign * mant1 * Math.pow(2, exp1 - 15);

    return f_unscaled;
}

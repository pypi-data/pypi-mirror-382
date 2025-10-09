import sangfroid.layer as sl
import sangfroid.value as v
import sangfroid.field as f

@sl.Layer.handles_type()
class Shade(sl.Layer):
    SYMBOL = '👓'

    ### {{{
    SYNFIG_VERSION = "0.2"

    z_depth              = f.ParamTagField(v.Real, 0.0,
                        )
    amount               = f.ParamTagField(v.Real, 0.75,
                        )
    blend_method         = f.ParamTagField(v.BlendMethod, v.BlendMethod.BEHIND,
                        )
    color                = f.ParamTagField(v.Color, (1.0, 1.0, 1.0, 1.0),
                        )
    origin               = f.ParamTagField(v.X_Y, (0.200000003, -0.200000003),
                        )
    size                 = f.ParamTagField(v.X_Y, (0.1000000015, 0.1000000015),
                        )
    type_                = f.ParamTagField(v.Integer, 1,
                        )
    invert               = f.ParamTagField(v.Bool, False,
                        )

    ### }}}

@sl.Layer.handles_type()
class Bevel(sl.Layer):
    SYMBOL = '🫴'

    ### {{{
    SYNFIG_VERSION = "0.2"

    z_depth              = f.ParamTagField(v.Real, 0.0,
                        )
    amount               = f.ParamTagField(v.Real, 0.75,
                        )
    blend_method         = f.ParamTagField(v.BlendMethod, v.BlendMethod.ONTO,
                        )
    type_                = f.ParamTagField(v.Integer, 1,
                        )
    color1               = f.ParamTagField(v.Color, (1.0, 1.0, 1.0, 1.0),
                        )
    color2               = f.ParamTagField(v.Color, (0.0, 0.0, 0.0, 1.0),
                        )
    angle                = f.ParamTagField(v.Angle, 135.0,
                        )
    depth                = f.ParamTagField(v.Real, 0.2,
                        )
    softness             = f.ParamTagField(v.Real, 0.1,
                        )
    use_luma             = f.ParamTagField(v.Bool, False,
                        )
    solid                = f.ParamTagField(v.Bool, False,
                        )
    fake_origin          = f.ParamTagField(v.X_Y, (0.0, 0.0),
                        )

    ### }}}

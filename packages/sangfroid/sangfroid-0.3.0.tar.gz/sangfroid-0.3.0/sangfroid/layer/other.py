import sangfroid.layer as sl
import sangfroid.value as v
import sangfroid.field as f

@sl.Layer.handles_type()
class Import(sl.Layer):
    SYMBOL = 'I'
    ### {{{
    SYNFIG_VERSION = "0.1"

    z_depth              = f.ParamTagField(v.Real, 0.0,
                        )
    amount               = f.ParamTagField(v.Real, 1.0,
                        )
    blend_method         = f.ParamTagField(v.BlendMethod, v.BlendMethod.COMPOSITE,
                        )
    tl                   = f.ParamTagField(v.X_Y, (-0.5333333611, 0.5333333611),
                        )
    br                   = f.ParamTagField(v.X_Y, (0.5333333611, -0.5333333611),
                        )
    c                    = f.ParamTagField(v.Integer, 1,
                        )
    gamma_adjust         = f.ParamTagField(v.Real, 1.0,
                        )
    filename             = f.ParamTagField(v.String, 'drop.png',
                        )
    time_offset          = f.ParamTagField(v.Time, 0,
                        )

    ### }}}

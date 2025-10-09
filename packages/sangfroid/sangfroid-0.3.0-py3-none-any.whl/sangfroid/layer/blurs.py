import sangfroid.layer as sl
import sangfroid.value as v
import sangfroid.field as f

@sl.Layer.handles_type()
class Blur(sl.Layer):
    SYMBOL = '🟠'

    ### {{{
    SYNFIG_VERSION = "0.3"

    z_depth              = f.ParamTagField(v.Real, 0.0,
                        )
    amount               = f.ParamTagField(v.Real, 1.0,
                        )
    blend_method         = f.ParamTagField(v.BlendMethod, v.BlendMethod.STRAIGHT,
                        )
    size                 = f.ParamTagField(v.X_Y, (0.1000000015, 0.1000000015),
                        )
    type_                = f.ParamTagField(v.Integer, 1,
                        )

    ### }}}

@sl.Layer.handles_type()
class Radial_Blur(sl.Layer):
    SYMBOL = '🟠'

    ### {{{
    SYNFIG_VERSION = "0.1"

    z_depth              = f.ParamTagField(v.Real, 0.0,
                        )
    amount               = f.ParamTagField(v.Real, 1.0,
                        )
    blend_method         = f.ParamTagField(v.BlendMethod, v.BlendMethod.STRAIGHT,
                        )
    origin               = f.ParamTagField(v.X_Y, (0.0, 0.0),
                        )
    size                 = f.ParamTagField(v.Real, 0.2,
                        )
    fade_out             = f.ParamTagField(v.Bool, False,
                        )

    ### }}}

@sl.Layer.handles_type()
class Motion_Blur(sl.Layer):
    SYMBOL = '🟠'

    ### {{{
    SYNFIG_VERSION = "0.2"

    aperture             = f.ParamTagField(v.Time, '1s',
                        )
    subsamples_factor    = f.ParamTagField(v.Real, 1.0,
                        )
    subsampling_type     = f.ParamTagField(v.Integer, 2,
                        )
    subsample_start      = f.ParamTagField(v.Real, 0.0,
                        )
    subsample_end        = f.ParamTagField(v.Real, 1.0,
                        )

    ### }}}

import sangfroid.layer as sl
import sangfroid.value as v
import sangfroid.field as f

@sl.Layer.handles_type()
class Timeloop(sl.Layer):
    SYMBOL = '🕰️'

    ### {{{
    SYNFIG_VERSION = "0.2"

    z_depth              = f.ParamTagField(v.Real, 0.0,
                        )
    link_time            = f.ParamTagField(v.Time, 0,
                        )
    local_time           = f.ParamTagField(v.Time, 0,
                        )
    duration             = f.ParamTagField(v.Time, '1s',
                        )
    only_for_positive_duration = f.ParamTagField(v.Bool, False,
                        )
    symmetrical          = f.ParamTagField(v.Bool, True,
                        )

    ### }}}

@sl.Layer.handles_type()
class Stroboscope(sl.Layer):
    SYMBOL = '🔦'

    ### {{{
    SYNFIG_VERSION = "0.1"

    z_depth              = f.ParamTagField(v.Real, 0.0,
                        )
    frequency            = f.ParamTagField(v.Real, 2.0,
                        )

    ### }}}

@sl.Layer.handles_type()
class Freetime(sl.Layer):
    SYMBOL = '🍦'
    
    ### {{{
    SYNFIG_VERSION = "0.1"

    z_depth              = f.ParamTagField(v.Real, 0.0,
                        )
    time                 = f.ParamTagField(v.Time, 0,
                        )

    ### }}}

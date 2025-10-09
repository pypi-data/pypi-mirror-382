import sangfroid.layer as sl
import sangfroid.value as v
import sangfroid.field as f

@sl.Layer.handles_type()
class Scale(sl.Layer):
    SYMBOL = '⚖️' # yeah, a bit contrived

    ### {{{
    PARAMS = {
        "amount": v.Real,
        "center": v.Vector,
    }












    ### }}}

@sl.Layer.handles_type()
class Zoom(Scale):
    ### {{{
    SYNFIG_VERSION = "0.1"

    amount               = f.ParamTagField(v.Real, 0.0,
                        )
    center               = f.ParamTagField(v.X_Y, (0.0, 0.0),
                        )

    ### }}}
    pass # XXX do they differ?

@sl.Layer.handles_type()
class Translate(sl.Layer):
    SYMBOL = '⇄'

    ### {{{
    SYNFIG_VERSION = "0.1"

    origin               = f.ParamTagField(v.X_Y, (0.0, 0.0),
                        )

    ### }}}

@sl.Layer.handles_type()
class Rotate(sl.Layer):
    SYMBOL = '🗘'

    ### {{{
    SYNFIG_VERSION = "0.1"

    origin               = f.ParamTagField(v.X_Y, (0.0, 0.0),
                        )
    amount               = f.ParamTagField(v.Angle, 0.0,
                        )

    ### }}}

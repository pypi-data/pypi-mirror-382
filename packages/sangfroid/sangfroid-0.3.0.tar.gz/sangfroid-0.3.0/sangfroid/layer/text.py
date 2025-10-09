from sangfroid.layer.layer import Layer
import sangfroid.value as v
import sangfroid.field as f

@Layer.handles_type()
class Text(Layer):
    SYMBOL = '𝕋'

    ### {{{
    SYNFIG_VERSION = "0.5"

    z_depth              = f.ParamTagField(v.Real, 0.0,
                        )
    amount               = f.ParamTagField(v.Real, 1.0,
                        )
    blend_method         = f.ParamTagField(v.BlendMethod, v.BlendMethod.COMPOSITE,
                        )
    text                 = f.ParamTagField(v.String, 'Hello wombat!',
                        )
    color                = f.ParamTagField(v.Color, (1.0, 1.0, 1.0, 1.0),
                        )
    family               = f.ParamTagField(v.String, 'Sans Serif',
                        )
    style                = f.ParamTagField(v.Integer, 0,
                        )
    weight               = f.ParamTagField(v.Integer, 400,
                        )
    direction            = f.ParamTagField(v.Integer, 0,
                        )
    compress             = f.ParamTagField(v.Real, 1.0,
                        )
    vcompress            = f.ParamTagField(v.Real, 1.0,
                        )
    size                 = f.ParamTagField(v.X_Y, (0.25, 0.25),
                        )
    orient               = f.ParamTagField(v.X_Y, (0.5, 0.5),
                        )
    origin               = f.ParamTagField(v.X_Y, (0.0, 0.0),
                        )
    use_kerning          = f.ParamTagField(v.Bool, True,
                        )
    grid_fit             = f.ParamTagField(v.Bool, False,
                        )
    invert               = f.ParamTagField(v.Bool, False,
                        )

    ### }}}

    def __init__(self, tag=None):
        new_text = None

        if isinstance(tag, str):
            new_text = tag
            tag = None

        super().__init__(tag)

        if new_text is not None:
            self.text = new_text

    def __repr__(self):
        result = super().__repr__()[:-1]
        result += ' ' + repr(self.text.value) + ']'

        return result

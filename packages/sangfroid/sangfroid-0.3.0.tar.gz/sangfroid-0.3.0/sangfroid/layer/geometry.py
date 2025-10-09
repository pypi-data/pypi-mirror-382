import sangfroid.layer as sl
import sangfroid.value as v
import sangfroid.field as f

@sl.Layer.handles_type()
class Star(sl.Layer):
    SYMBOL = '⭐'

    ### {{{
    SYNFIG_VERSION = "0.1"

    z_depth              = f.ParamTagField(v.Real, 0.0,
                        )
    amount               = f.ParamTagField(v.Real, 1.0,
                        )
    blend_method         = f.ParamTagField(v.BlendMethod, v.BlendMethod.COMPOSITE,
                        )
    color                = f.ParamTagField(v.Color, (1.0, 1.0, 1.0, 1.0),
                        )
    origin               = f.ParamTagField(v.X_Y, (0.0, 0.0),
                        )
    invert               = f.ParamTagField(v.Bool, False,
                        )
    antialias            = f.ParamTagField(v.Bool, True,
                        )
    feather              = f.ParamTagField(v.Real, 0.0,
                        )
    blurtype             = f.ParamTagField(v.Integer, 1,
                        )
    winding_style        = f.ParamTagField(v.Integer, 0,
                        )
    radius1              = f.ParamTagField(v.Real, 1.0,
                        )
    radius2              = f.ParamTagField(v.Real, 0.38,
                        )
    angle                = f.ParamTagField(v.Angle, 90.0,
                        )
    points               = f.ParamTagField(v.Integer, 5,
                        )
    regular_polygon      = f.ParamTagField(v.Bool, False,
                        )

    ### }}}

@sl.Layer.handles_type()
class Solid_Color(sl.Layer):
    SYMBOL = '▊'

    ### {{{
    SYNFIG_VERSION = "0.1"

    z_depth              = f.ParamTagField(v.Real, 0.0,
                        )
    amount               = f.ParamTagField(v.Real, 1.0,
                        )
    blend_method         = f.ParamTagField(v.BlendMethod, v.BlendMethod.COMPOSITE,
                        )
    color                = f.ParamTagField(v.Color, (1.0, 1.0, 1.0, 1.0),
                        )

    ### }}}

@sl.Layer.handles_type()
class Region(sl.Layer):
    SYMBOL = '🟤'

    ### {{{
    SYNFIG_VERSION = "0.1"

    z_depth              = f.ParamTagField(v.Real, 0.0,
                        )
    amount               = f.ParamTagField(v.Real, 1.0,
                        )
    blend_method         = f.ParamTagField(v.BlendMethod, v.BlendMethod.COMPOSITE,
                        )
    color                = f.ParamTagField(v.Color, (1.0, 1.0, 1.0, 1.0),
                        )
    origin               = f.ParamTagField(v.X_Y, (0.0, 0.0),
                        )
    invert               = f.ParamTagField(v.Bool, False,
                        )
    antialias            = f.ParamTagField(v.Bool, True,
                        )
    feather              = f.ParamTagField(v.Real, 0.0,
                        )
    blurtype             = f.ParamTagField(v.Integer, 1,
                        )
    winding_style        = f.ParamTagField(v.Integer, 0,
                        )
    bline                = f.NotImplementedField("Bline",
                        )

    ### }}}

@sl.Layer.handles_type()
class Rectangle(sl.Layer):
    SYMBOL = '🟦'

    ### {{{
    SYNFIG_VERSION = "0.2"

    z_depth              = f.ParamTagField(v.Real, 0.0,
                        )
    amount               = f.ParamTagField(v.Real, 1.0,
                        )
    blend_method         = f.ParamTagField(v.BlendMethod, v.BlendMethod.COMPOSITE,
                        )
    color                = f.ParamTagField(v.Color, (1.0, 1.0, 1.0, 1.0),
                        )
    point1               = f.ParamTagField(v.X_Y, (0.0, 0.0),
                        )
    point2               = f.ParamTagField(v.X_Y, (1.0, 1.0),
                        )
    expand               = f.ParamTagField(v.Real, 0.0,
                        )
    invert               = f.ParamTagField(v.Bool, False,
                        )
    feather_x            = f.ParamTagField(v.Real, 0.0,
                        )
    feather_y            = f.ParamTagField(v.Real, 0.0,
                        )
    bevel                = f.ParamTagField(v.Real, 0.0,
                        )
    bevCircle            = f.ParamTagField(v.Bool, True,
                        )

    ### }}}

@sl.Layer.handles_type()
class Polygon(sl.Layer):
    SYMBOL = '⭓'

    ### {{{
    SYNFIG_VERSION = "0.1"

    z_depth              = f.ParamTagField(v.Real, 0.0,
                        )
    amount               = f.ParamTagField(v.Real, 1.0,
                        )
    blend_method         = f.ParamTagField(v.BlendMethod, v.BlendMethod.COMPOSITE,
                        )
    color                = f.ParamTagField(v.Color, (1.0, 1.0, 1.0, 1.0),
                        )
    origin               = f.ParamTagField(v.X_Y, (0.0, 0.0),
                        )
    invert               = f.ParamTagField(v.Bool, False,
                        )
    antialias            = f.ParamTagField(v.Bool, True,
                        )
    feather              = f.ParamTagField(v.Real, 0.0,
                        )
    blurtype             = f.ParamTagField(v.Integer, 1,
                        )
    winding_style        = f.ParamTagField(v.Integer, 0,
                        )
    vector_list          = f.NotImplementedField("Dynamic_List",
                        )

    ### }}}

@sl.Layer.handles_type()
class Outline(sl.Layer):
    SYMBOL = '⭔'

    ### {{{
    SYNFIG_VERSION = "0.3"

    z_depth              = f.ParamTagField(v.Real, 0.0,
                        )
    amount               = f.ParamTagField(v.Real, 1.0,
                        )
    blend_method         = f.ParamTagField(v.BlendMethod, v.BlendMethod.COMPOSITE,
                        )
    color                = f.ParamTagField(v.Color, (0.0, 0.0, 0.0, 1.0),
                        )
    origin               = f.ParamTagField(v.X_Y, (0.0, 0.0),
                        )
    invert               = f.ParamTagField(v.Bool, False,
                        )
    antialias            = f.ParamTagField(v.Bool, True,
                        )
    feather              = f.ParamTagField(v.Real, 0.0,
                        )
    blurtype             = f.ParamTagField(v.Integer, 1,
                        )
    winding_style        = f.ParamTagField(v.Integer, 0,
                        )
    bline                = f.NotImplementedField("Bline",
                        )
    width                = f.ParamTagField(v.Real, 0.0166666667,
                        )
    expand               = f.ParamTagField(v.Real, 0.0,
                        )
    sharp_cusps          = f.ParamTagField(v.Bool, True,
                        )
    round_tip            = f.ParamArrayField(v.Bool, True,
                        )
    homogeneous_width    = f.ParamTagField(v.Bool, True,
                        )

    ### }}}

@sl.Layer.handles_type()
class Circle(sl.Layer):
    SYMBOL = '🔵'

    ### {{{
    SYNFIG_VERSION = "0.2"

    z_depth              = f.ParamTagField(v.Real, 0.0,
                        )
    amount               = f.ParamTagField(v.Real, 1.0,
                        )
    blend_method         = f.ParamTagField(v.BlendMethod, v.BlendMethod.COMPOSITE,
                        )
    color                = f.ParamTagField(v.Color, (1.0, 1.0, 1.0, 1.0),
                        )
    radius               = f.ParamTagField(v.Real, 1.0,
                        )
    feather              = f.ParamTagField(v.Real, 0.0,
                        )
    origin               = f.ParamTagField(v.X_Y, (0.0, 0.0),
                        )
    invert               = f.ParamTagField(v.Bool, False,
                        )

    ### }}}

@sl.Layer.handles_type()
class Checker_Board(sl.Layer):
    SYMBOL = '🙾'

    ### {{{
    SYNFIG_VERSION = "0.2"

    z_depth              = f.ParamTagField(v.Real, 0.0,
                        )
    amount               = f.ParamTagField(v.Real, 1.0,
                        )
    blend_method         = f.ParamTagField(v.BlendMethod, v.BlendMethod.COMPOSITE,
                        )
    color                = f.ParamTagField(v.Color, (1.0, 1.0, 1.0, 1.0),
                        )
    origin               = f.ParamTagField(v.X_Y, (0.125, 0.125),
                        )
    size                 = f.ParamTagField(v.X_Y, (0.25, 0.25),
                        )
    antialias            = f.ParamTagField(v.Bool, True,
                        )

    ### }}}

@sl.Layer.handles_type()
class Advanced_Outline(sl.Layer):
    SYMBOL = '⬡'

    ### {{{
    SYNFIG_VERSION = "0.3"

    z_depth              = f.ParamTagField(v.Real, 0.0,
                        )
    amount               = f.ParamTagField(v.Real, 1.0,
                        )
    blend_method         = f.ParamTagField(v.BlendMethod, v.BlendMethod.COMPOSITE,
                        )
    color                = f.ParamTagField(v.Color, (0.0, 0.0, 0.0, 1.0),
                        )
    origin               = f.ParamTagField(v.X_Y, (0.0, 0.0),
                        )
    invert               = f.ParamTagField(v.Bool, False,
                        )
    antialias            = f.ParamTagField(v.Bool, True,
                        )
    feather              = f.ParamTagField(v.Real, 0.0,
                        )
    blurtype             = f.ParamTagField(v.Integer, 1,
                        )
    winding_style        = f.ParamTagField(v.Integer, 0,
                        )
    bline                = f.NotImplementedField("Bline",
                        )
    width                = f.ParamTagField(v.Real, 0.0166666667,
                        )
    expand               = f.ParamTagField(v.Real, 0.0,
                        )
    start_tip            = f.ParamTagField(v.Integer, 1,
                        )
    end_tip              = f.ParamTagField(v.Integer, 1,
                        )
    cusp_type            = f.ParamTagField(v.Integer, 0,
                        )
    smoothness           = f.ParamTagField(v.Real, 1.0,
                        )
    homogeneous          = f.ParamTagField(v.Bool, True,
                        )
    wplist               = f.NotImplementedField("Wplist",
                        )
    dash_enabled         = f.ParamTagField(v.Bool, False,
                        )
    dilist               = f.NotImplementedField("Dilist",
                        )
    dash_offset          = f.ParamTagField(v.Real, 0.0,
                        )

    ### }}}

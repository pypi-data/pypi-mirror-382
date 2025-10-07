import openmdao.api as om
from openaerostruct.structures.section_properties_tube import SectionPropertiesTube
from openaerostruct.geometry.radius_comp import RadiusComp
from openaerostruct.utils.interpolation import get_normalized_span_coords


class TubeGroup(om.Group):
    """Group that contains everything needed for a structural-only problem."""

    def initialize(self):
        self.options.declare("surface", types=dict)
        self.options.declare("connect_geom_DVs", default=True)
        # The option "connect_geom_DVs" is no longer necessary, but we still keep it to be backward compatible.

    def setup(self):
        surface = self.options["surface"]

        if "thickness_cp" in surface.keys():
            n_cp = len(surface["thickness_cp"])
            # Add bspline components for active bspline geometric variables.
            x_interp = get_normalized_span_coords(surface, mid_panel=True)
            comp = self.add_subsystem(
                "thickness_bsp",
                om.SplineComp(
                    method="bsplines",
                    x_interp_val=x_interp,
                    num_cp=n_cp,
                    interp_options={"order": min(n_cp, 4), "x_cp_start": 0, "x_cp_end": 1},
                ),
                promotes_inputs=["thickness_cp"],
                promotes_outputs=["thickness"],
            )
            comp.add_spline(y_cp_name="thickness_cp", y_interp_name="thickness", y_units="m")
            self.set_input_defaults("thickness_cp", val=surface["thickness_cp"], units="m")

        if "radius_cp" in surface.keys():
            n_cp = len(surface["radius_cp"])
            # Add bspline components for active bspline geometric variables.
            x_interp = get_normalized_span_coords(surface, mid_panel=True)
            comp = self.add_subsystem(
                "radius_bsp",
                om.SplineComp(
                    method="bsplines",
                    x_interp_val=x_interp,
                    num_cp=n_cp,
                    interp_options={"order": min(n_cp, 4), "x_cp_start": 0, "x_cp_end": 1},
                ),
                promotes_inputs=["radius_cp"],
                promotes_outputs=["radius"],
            )
            comp.add_spline(y_cp_name="radius_cp", y_interp_name="radius", y_units="m")
            self.set_input_defaults("radius_cp", val=surface["radius_cp"], units="m")

        else:
            self.add_subsystem(
                "radius_comp",
                RadiusComp(surface=surface),
                promotes_inputs=["mesh", "t_over_c"],
                promotes_outputs=["radius"],
            )

        self.add_subsystem(
            "tube",
            SectionPropertiesTube(surface=surface),
            promotes_inputs=["thickness", "radius"],
            promotes_outputs=["A", "Iy", "Iz", "J"],
        )

import openmdao.api as om

from openmdao.utils.assert_utils import assert_check_partials
import numpy as np
from openaerostruct.meshing.mesh_generator import generate_mesh


def assert_opt_successful(test, optResult):
    """Check whether an OpenMDAO optimization successfully converged

    Parameters
    ----------
    test : unittest.TestCase
        The test case that is being run
    optResult :
        Result returned by OpenMDAO's run_driver() method
    """
    # In older versions of OpenMDAO, the run_driver() method returns a boolean that indicates whether the
    # optimization failed, but in newer versions it returns an object that contains the optimization results,
    # including a `success` attribute.
    if isinstance(optResult, bool):
        test.assertFalse(optResult)
    else:
        test.assertTrue(optResult.success)


def view_mat(mat1, mat2=None, key="Title", tol=1e-10):  # pragma: no cover
    """
    Helper function used to visually examine matrices. It plots mat1 and mat2 side by side,
    and shows the difference between the two.

    Parameters
    ----------
    mat1 : numpy array
        The Jacobian approximated by openMDAO
    mat2 : numpy array
        The Jacobian computed by compute_partials
    key : str
        The name of the tuple (of, wrt) for which the Jacobian is computed
    tol : float (Optional)
        The tolerance, below which the two numbers are considered the same for
        plotting purposes.

    """
    import matplotlib.pyplot as plt

    if len(mat1.shape) > 2:
        mat1 = np.sum(mat1, axis=2)
    if mat2 is not None:
        if len(mat2.shape) > 2:
            mat2 = np.sum(mat2, axis=2)
        vmin = np.amin(np.hstack((mat1.flatten(), mat2.flatten())))
        vmax = np.amax(np.hstack((mat1.flatten(), mat2.flatten())))
    else:
        vmin = np.amin(np.hstack((mat1.flatten())))
        vmax = np.amax(np.hstack((mat1.flatten())))
    if vmax - vmin < tol:  # add small difference for plotting if both values are the same
        vmin = vmin - tol
        vmax = vmax + tol

    if mat2 is not None:
        fig, ax = plt.subplots(ncols=3, figsize=(12, 6))
        ax[0].imshow(mat1.real, interpolation="none", vmin=vmin, vmax=vmax)
        ax[0].set_title("Approximated Jacobian")

        im = ax[1].imshow(mat2.real, interpolation="none", vmin=vmin, vmax=vmax)
        fig.colorbar(im, orientation="horizontal", ax=ax[0:2].ravel().tolist())
        ax[1].set_title("User-Defined Jacobian")

        diff = mat2.real - mat1.real
        if np.max(np.abs(diff).flatten()) < tol:  # add small difference for plotting if diff is small
            vmin = -1 * tol
            vmax = tol
        im2 = ax[2].imshow(diff, interpolation="none", vmin=vmin, vmax=vmax)
        fig.colorbar(im2, orientation="horizontal", ax=ax[2], aspect=10)
        ax[2].set_title("Difference")

    else:
        mtx = np.hstack((mat1.flatten()))
        vmin = np.nanmin(mtx[mtx != -np.inf])
        vmax = np.nanmax(mtx[mtx != np.inf])
        print(vmin, vmax)
        fig = plt.figure(figsize=(12, 6))
        ax = plt.gca()
        im = plt.imshow(mat1.real, interpolation="none", vmin=vmin, vmax=vmax)
        fig.colorbar(im, orientation="horizontal", ax=ax, aspect=10)
        plt.title("Jacobian")

    plt.suptitle(key)
    plt.show()


def run_test(
    test_obj,
    comp,
    complex_flag=False,
    compact_print=True,
    method="fd",
    step=1e-6,
    atol=1e-5,
    rtol=1e-5,
    view=False,
    reports=False,
):
    prob = om.Problem(reports=reports)
    prob.model.add_subsystem("comp", comp)
    prob.setup(force_alloc_complex=complex_flag)

    prob.run_model()

    if method == "cs":
        step = 1e-40

    check = prob.check_partials(compact_print=compact_print, method=method, step=step)

    if view:
        # Loop through this `check` dictionary and visualize the approximated
        # and computed derivatives
        for key, subjac in check[list(check.keys())[0]].items():
            view_mat(subjac["J_fd"], subjac["J_fwd"], key)

    assert_check_partials(check, atol=atol, rtol=rtol)

    return prob


def get_default_surfaces():
    # Create a dictionary to store options about the mesh
    mesh_dict = {"num_y": 7, "num_x": 2, "wing_type": "CRM", "symmetry": True, "num_twist_cp": 5}

    # Generate the aerodynamic mesh based on the previous dictionary
    mesh, twist_cp = generate_mesh(mesh_dict)

    wing_dict = {
        "name": "wing",
        "num_y": 4,
        "num_x": 2,
        "symmetry": True,
        "groundplane": False,
        "S_ref_type": "wetted",
        "CL0": 0.1,
        "CD0": 0.1,
        "mesh": mesh,
        # Airfoil properties for viscous drag calculation
        "k_lam": 0.05,  # percentage of chord with laminar
        # flow, used for viscous drag
        "t_over_c_cp": np.array([0.15]),  # thickness over chord ratio (NACA0015)
        "c_max_t": 0.303,  # chordwise location of maximum (NACA0015)
        # thickness
        "with_viscous": True,  # if true, compute viscous drag
        "with_wave": False,  # if true, computes wave drag
        "fem_model_type": "tube",
        # Structural values are based on aluminum 7075
        "E": 70.0e9,  # [Pa] Young's modulus of the spar
        "G": 30.0e9,  # [Pa] shear modulus of the spar
        "yield": 500.0e6,
        "safety_factor": 2.5,  # [Pa] yield stress divided by 2.5 for limiting case
        "mrho": 3.0e3,  # [kg/m^3] material density
        "fem_origin": 0.35,  # normalized chordwise location of the spar
        "wing_weight_ratio": 2.0,
        "struct_weight_relief": False,  # True to add the weight of the structure to the loads on the structure
        "distributed_fuel_weight": False,  # True to add the weight of the structure to the loads on the structure
        "Wf_reserve": 10000.0,
    }

    # Create a dictionary to store options about the mesh
    mesh_dict = {"num_y": 5, "num_x": 3, "wing_type": "rect", "symmetry": False}

    # Generate the aerodynamic mesh based on the previous dictionary
    mesh = generate_mesh(mesh_dict)

    tail_dict = {"name": "tail", "num_y": 5, "num_x": 3, "symmetry": False, "mesh": mesh}

    surfaces = [wing_dict, tail_dict]

    return surfaces


def get_ground_effect_surfaces():
    # Create a dictionary to store options about the mesh
    mesh_dict = {"num_y": 7, "num_x": 2, "wing_type": "CRM", "symmetry": True, "num_twist_cp": 5}

    # Generate the aerodynamic mesh based on the previous dictionary
    mesh, twist_cp = generate_mesh(mesh_dict)

    wing_dict = {
        "name": "wing",
        "num_y": 4,
        "num_x": 2,
        "symmetry": True,
        "groundplane": True,
        "S_ref_type": "wetted",
        "CL0": 0.1,
        "CD0": 0.1,
        "mesh": mesh,
        # Airfoil properties for viscous drag calculation
        "k_lam": 0.05,  # percentage of chord with laminar
        # flow, used for viscous drag
        "t_over_c_cp": np.array([0.15]),  # thickness over chord ratio (NACA0015)
        "c_max_t": 0.303,  # chordwise location of maximum (NACA0015)
        # thickness
        "with_viscous": True,  # if true, compute viscous drag
        "with_wave": False,  # if true, computes wave drag
        "fem_model_type": "tube",
        # Structural values are based on aluminum 7075
        "E": 70.0e9,  # [Pa] Young's modulus of the spar
        "G": 30.0e9,  # [Pa] shear modulus of the spar
        "yield": 500.0e6,
        "safety_factor": 2.5,  # [Pa] yield stress divided by 2.5 for limiting case
        "mrho": 3.0e3,  # [kg/m^3] material density
        "fem_origin": 0.35,  # normalized chordwise location of the spar
        "wing_weight_ratio": 2.0,
        "struct_weight_relief": False,  # True to add the weight of the structure to the loads on the structure
        "distributed_fuel_weight": False,  # True to add the weight of the structure to the loads on the structure
        "Wf_reserve": 10000.0,
    }

    # Create a dictionary to store options about the mesh
    mesh_dict = {"num_y": 5, "num_x": 3, "wing_type": "rect", "symmetry": True}

    # Generate the aerodynamic mesh based on the previous dictionary
    mesh = generate_mesh(mesh_dict)

    tail_dict = {"name": "tail", "num_y": 3, "num_x": 3, "symmetry": True, "groundplane": True, "mesh": mesh}

    surfaces = [wing_dict, tail_dict]

    return surfaces


def get_three_section_surface(sym=True, visc=False):
    # Outputs a three section wing surface
    # Set-up B-splines for each section. Done here since this information will be needed multiple times.
    sec_chord_cp = [np.ones(2), np.ones(2), np.ones(2)]

    if sym:
        span = [0.5, 0.5, 0.5]
    else:
        span = [1.0, 1.0, 1.0]

    surface_dict = {
        # Wing definition
        # Basic surface parameters
        "name": "surface",
        "is_multi_section": True,
        "num_sections": 3,  # The number of sections in the multi-section surface
        "sec_name": ["sec0", "sec1", "sec2"],  # names of the individual sections
        "symmetry": sym,  # if true, model one half of wing. reflected across the midspan of the root section
        "S_ref_type": "wetted",  # how we compute the wing area,
        # can be 'wetted' or 'projected'
        # Geometry Parameters
        "taper": [1.0, 1.0, 1.0],  # Wing taper for each section
        "span": span,  # Wing span for each section
        "sweep": [0.0, 0, 0.0],  # Wing sweep for each section
        "dihedral": [0.0, 0.0, 0.0],
        "twist_cp": [np.zeros(2), np.zeros(2), np.zeros(2)],
        "chord_cp": sec_chord_cp,
        "ref_axis_pos": 0.25,
        "root_chord": 1.0,  # Wing root chord for each section
        # Mesh Parameters
        "meshes": "gen-meshes",  # Supply a mesh for each section or "gen-meshes" for automatic mesh generation
        "nx": 2,  # Number of chordwise points. Same for all sections
        "ny": [11, 11, 11],  # Number of spanwise points for each section
        # Aerodynamic Parameters
        "CL0": 0.0,  # CL of the surface at alpha=0
        "CD0": 0.015,  # CD of the surface at alpha=0
        # Airfoil properties for viscous drag calculation
        "k_lam": 0.05,  # percentage of chord with laminar
        # flow, used for viscous drag
        "t_over_c_cp": [
            np.array([0.15]),
            np.array([0.15]),
            np.array([0.15]),
        ],  # thickness over chord ratio (NACA0015)
        "c_max_t": 0.303,  # chordwise location of maximum (NACA0015)
        # thickness
        "with_viscous": visc,  # if true, compute viscous drag
        "with_wave": False,  # if true, compute wave drag
        "groundplane": False,
    }

    if sym is False:
        surface_dict["root_section"] = 1

    if visc is True:
        surface_dict["t_over_c_cp"] = [np.array([0.15]), np.array([0.15])]
        surface_dict["nx"] = 3

    return surface_dict, sec_chord_cp


def get_two_section_surface(sym=True, visc=False):
    # Outputs a symmetric two section wing surface
    # Set-up B-splines for each section. Done here since this information will be needed multiple times.
    sec_chord_cp = [np.array([1.0, 1.0]), np.array([1.0, 1.0])]

    if sym:
        span = [0.5, 0.5]
    else:
        span = [1.0, 1.0]

    # Create a dictionary with info and options about the multi-section aerodynamic
    # lifting surface
    surface_dict = {
        # Wing definition
        # Basic surface parameters
        "name": "surface",
        "is_multi_section": True,
        "num_sections": 2,  # The number of sections in the multi-section surface
        "sec_name": ["sec0", "sec1"],  # names of the individual sections
        "symmetry": sym,  # if true, model one half of wing. reflected across the midspan of the root section
        "S_ref_type": "wetted",  # how we compute the wing area, can be 'wetted' or 'projected'
        "root_section": 1,
        # Geometry Parameters
        "taper": [1.0, 1.0],  # Wing taper for each section
        "span": span,  # Wing span for each section
        "sweep": [0.0, 0.0],  # Wing sweep for each section
        "chord_cp": sec_chord_cp,
        "twist_cp": [np.zeros(2), np.zeros(2)],
        # "chord_cp": [np.ones(1),2*np.ones(1),3*np.ones(1)], #Chord B-spline control points for each section
        "ref_axis_pos": 0.25,
        "root_chord": 1.0,  # Wing root chord for each section
        # Mesh Parameters
        "meshes": "gen-meshes",  # Supply a mesh for each section or "gen-meshes" for automatic mesh generation
        "nx": 2,  # Number of chordwise points. Same for all sections
        "ny": [21, 21],  # Number of spanwise points for each section
        # Aerodynamic Parameters
        "CL0": 0.0,  # CL of the surface at alpha=0
        "CD0": 0.015,  # CD of the surface at alpha=0
        # Airfoil properties for viscous drag calculation
        "k_lam": 0.05,  # percentage of chord with laminar
        # flow, used for viscous drag
        # "t_over_c_cp": [np.array([0.15]),np.array([0.15])],  # thickness over chord ratio (NACA0015)
        "c_max_t": 0.303,  # chordwise location of maximum (NACA0015)
        # thickness
        "with_viscous": visc,  # if true, compute viscous drag
        "with_wave": False,  # if true, compute wave drag
        "groundplane": False,
    }

    if sym is False:
        surface_dict["root_section"] = 1

    if visc is True:
        surface_dict["t_over_c_cp"] = [np.array([0.15]), np.array([0.15])]
        surface_dict["nx"] = 3

    return surface_dict, sec_chord_cp


def get_single_section_surface():
    """Create a dictionary with info and options about the aerodynamic
    single section lifting surface
    """

    # Create a dictionary to store options about the mesh
    mesh_dict = {
        "num_y": 81,
        "num_x": 2,
        "wing_type": "rect",
        "span": 2.0,
        "root_chord": 1.0,
        "symmetry": True,
        "span_cos_spacing": 0,
        "chord_cos_spacing": 0,
    }

    # Generate the aerodynamic mesh based on the previous dictionary
    mesh = generate_mesh(mesh_dict)
    surface_dict = {
        # Wing definition
        "name": "surface",  # name of the surface
        "symmetry": True,  # if true, model one half of wing
        # reflected across the plane y = 0
        "S_ref_type": "wetted",  # how we compute the wing area,
        # can be 'wetted' or 'projected'
        "twist_cp": np.zeros(2),
        "mesh": mesh,
        "CL0": 0.0,  # CL of the surface at alpha=0
        "CD0": 0.015,  # CD of the surface at alpha=0
        # Airfoil properties for viscous drag calculation
        "k_lam": 0.05,  # percentage of chord with laminar
        # flow, used for viscous drag
        "c_max_t": 0.303,  # chordwise location of maximum (NACA0015)
        # thickness
        "ref_axis_pos": 0.25,
        "with_viscous": False,  # if true, compute viscous drag
        "with_wave": False,  # if true, compute wave drag
        "groundplane": False,
    }

    return surface_dict


def get_two_section_surface_AS(sym=True):
    # Outputs a symmetric two section wing surface
    # Set-up B-splines for each section. Done here since this information will be needed multiple times.
    sec_twist_cp = [np.array([0.0, 0.0]), np.array([0.0, 0.0])]

    if sym:
        span = [10.0, 10.0]
    else:
        span = [20.0, 20.0]

    # Create a dictionary with info and options about the multi-section aerodynamic
    # lifting surface
    surface_dict = {
        # Wing definition
        # Basic surface parameters
        "name": "surface",
        "is_multi_section": True,
        "num_sections": 2,  # The number of sections in the multi-section surface
        "sec_name": ["sec0", "sec1"],  # names of the individual sections
        "symmetry": sym,  # if true, model one half of wing. reflected across the midspan of the root section
        "S_ref_type": "wetted",  # how we compute the wing area, can be 'wetted' or 'projected'
        "root_section": 1,
        # Geometry Parameters
        "taper": [1.0, 1.0],  # Wing taper for each section
        "span": span,  # Wing span for each section
        "sweep": [0.0, 0.0],  # Wing sweep for each section
        "twist_cp": sec_twist_cp,
        "t_over_c_cp": [np.array([0.15]), np.array([0.15])],
        "root_chord": 5.0,  # Wing root chord for each section
        # Mesh Parameters
        "meshes": "gen-meshes",  # Supply a mesh for each section or "gen-meshes" for automatic mesh generation
        "nx": 2,  # Number of chordwise points. Same for all sections
        "ny": [3, 3],  # Number of spanwise points for each section
        # Aerodynamic Parameters
        "CL0": 0.0,  # CL of the surface at alpha=0
        "CD0": 0.015,  # CD of the surface at alpha=0
        # Airfoil properties for viscous drag calculation
        "k_lam": 0.05,  # percentage of chord with laminar
        # flow, used for viscous drag
        # "t_over_c_cp": [np.array([0.15]),np.array([0.15])],  # thickness over chord ratio (NACA0015)
        "c_max_t": 0.303,  # chordwise location of maximum (NACA0015)
        # thickness
        "with_viscous": True,  # if true, compute viscous drag
        "with_wave": False,  # if true, compute wave drag
        "groundplane": False,
        # Structural
        "fem_model_type": "tube",
        "thickness_cp": 0.1 * np.ones(2),
        "E": 70.0e9,  # [Pa] Young's modulus of the spar
        "G": 30.0e9,  # [Pa] shear modulus of the spar
        "yield": 500.0e6 / 2.5,  # [Pa] yield stress divided by 2.5 for limiting case
        "mrho": 3.0e3,  # [kg/m^3] material density
        "fem_origin": 0.35,  # normalized chordwise location of the spar
        "wing_weight_ratio": 2.0,
        "struct_weight_relief": False,  # True to add the weight of the structure to the loads on the structure
        "distributed_fuel_weight": False,
        # Constraints
        "exact_failure_constraint": False,  # if false, use KS function
    }

    if sym is False:
        surface_dict["root_section"] = 1

    return surface_dict, sec_twist_cp


def get_single_section_surface_AS():
    """Create a dictionary with info and options about the aerodynamic
    single section lifting surface
    """

    # Create a dictionary to store options about the mesh
    mesh_dict = {
        "num_y": 9,
        "num_x": 2,
        "wing_type": "rect",
        "span": 40.0,
        "root_chord": 5.0,
        "symmetry": True,
        "span_cos_spacing": 0.0,
        "chord_cos_spacing": 0.0,
    }

    # Generate the aerodynamic mesh based on the previous dictionary
    mesh = generate_mesh(mesh_dict)
    surface_dict = {
        # Wing definition
        "name": "surface",  # name of the surface
        "symmetry": True,  # if true, model one half of wing
        # reflected across the plane y = 0
        "S_ref_type": "wetted",  # how we compute the wing area,
        # can be 'wetted' or 'projected'
        "fem_model_type": "tube",
        "thickness_cp": np.ones((2)) * 0.1,
        "twist_cp": np.ones((3)),
        "mesh": mesh,
        # Aerodynamic performance of the lifting surface at
        # an angle of attack of 0 (alpha=0).
        # These CL0 and CD0 values are added to the CL and CD
        # obtained from aerodynamic analysis of the surface to get
        # the total CL and CD.
        # These CL0 and CD0 values do not vary wrt alpha.
        "CL0": 0.0,  # CL of the surface at alpha=0
        "CD0": 0.015,  # CD of the surface at alpha=0
        # Airfoil properties for viscous drag calculation
        "k_lam": 0.05,  # percentage of chord with laminar
        # flow, used for viscous drag
        "t_over_c_cp": np.array([0.15]),  # thickness over chord ratio (NACA0015)
        "c_max_t": 0.303,  # chordwise location of maximum (NACA0015)
        # thickness
        "with_viscous": True,
        "with_wave": False,  # if true, compute wave drag
        # Structural values are based on aluminum 7075
        "E": 70.0e9,  # [Pa] Young's modulus of the spar
        "G": 30.0e9,  # [Pa] shear modulus of the spar
        "yield": 500.0e6 / 2.5,  # [Pa] yield stress divided by 2.5 for limiting case
        "mrho": 3.0e3,  # [kg/m^3] material density
        "fem_origin": 0.35,  # normalized chordwise location of the spar
        "wing_weight_ratio": 2.0,
        "struct_weight_relief": False,  # True to add the weight of the structure to the loads on the structure
        "distributed_fuel_weight": False,
        # Constraints
        "exact_failure_constraint": False,  # if false, use KS function
    }

    return surface_dict

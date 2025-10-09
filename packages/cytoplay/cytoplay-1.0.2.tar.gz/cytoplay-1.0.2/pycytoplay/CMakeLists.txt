cmake_minimum_required(VERSION 3.14.0)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS ON)
set(CMAKE_BUILD_TYPE Release)

project("cytosim" C CXX)

set(PYSIM_LIBRARY_NAME "cytosim")
set(PYPLAY_LIBRARY_NAME "cytoplay")

set(SIM_LIBRARY "cytosimS")
set(SIMG_LIBRARY "cytosimG")
set(BASE_LIBRARY "cytobase")
set(MATH_LIBRARY "cytomath")
set(DISP_LIBRARY "cytodisp")
message(STATUS "              |     CMAKE_INSTALL_PREFIX: ${CMAKE_INSTALL_PREFIX}")

if(DEFINED DIMENSION)
    add_compile_definitions(DIM=${DIMENSION})
    set(SIM_LIBRARY "cytolibD${DIMENSION}")
    set(SIMG_LIBRARY "cytospaceD${DIMENSION}G")
    set(PY_LIBRARY_NAME "${PY_LIBRARY_NAME}${DIMENSION}D")
    set(PYSIM_LIBRARY_NAME "${PYSIM_LIBRARY_NAME}${DIMENSION}D")
    set(PYPLAY_LIBRARY_NAME "${PYPLAY_LIBRARY_NAME}${DIMENSION}D")
    set(SIM_TARGET "sim${DIMENSION}D")
    set(PLAY_TARGET "play${DIMENSION}D")

endif()

option(MAKE_SIM "build the simulation executable" ON)
option(MAKE_PLAY "build the graphical OpenGL viewer" ON)
option(MAKE_TOOLS "build all cytosim/tools executables" OFF)
option(MAKE_TESTS "build all cytosim/test executables" OFF)

#-------------------------------- Libraries ------------------------------------

if(NOT UNIX)
    message(WARNING "CMake File currently only setup to build on Linux and Mac")
elseif(APPLE)
    message(">>>>>> Building for APPLE")
else()
    message(">>>>>> Building for Linux")
    link_libraries("gfortran")
endif()

find_package(ZLIB REQUIRED)
# static linking preferred here:
find_package(BLAS)
find_library(BLAS_LIB libblas.a blas BLAS_LIBRARIES PATHS ~/lib REQUIRED)
if(BLAS_LIB)
    message(">>>>>> BLAS: ${BLAS_LIB}")
else()
    message(FATAL_ERROR "BLAS library not found")
endif()

find_package(LAPACK)
find_library(LAPACK_LIB liblapack.a lapack LAPACK_LIBRARIES PATHS ~/lib REQUIRED)
if(LAPACK_LIB)
    message(">>>>>> LAPACK: ${LAPACK_LIB}")
else()
    message(FATAL_ERROR "LAPACK library not found")
endif()

set(LAPACK_BLAS "${LAPACK_LIB}" "${BLAS_LIB}")

set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)

find_package(Curses REQUIRED)
include_directories(${CURSES_INCLUDE_DIR})


#-------------------------- Graphical Libraries --------------------------------

if(MAKE_PLAY)
    if(NOT APPLE)
        find_package(OpenGL REQUIRED COMPONENTS OpenGL)
        find_package(GLEW)
        find_package(GLUT)
        find_package(X11)
        find_package(Xt)
        set(OPENGL_LIBS
            OpenGL::GL
            GLEW
            glut
            X11
            Xt
        )
    elseif(UNIX AND APPLE)
        set(OPENGL_LIBS
            "-framework Accelerate"
            "-framework GLUT"
            "-framework OpenGL"
            "-framework AGL"
        )
    endif()
endif()


if ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
    set(FAST_FLAGS -Wno-deprecated-declarations -ffast-math -funroll-loops)
    set(DEBUG_FLAGS -g3 -ggdb)
elseif ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "AppleClang")
    set(FAST_FLAGS -Wno-deprecated-declarations -ffast-math -funroll-loops)
    set(DEBUG_FLAGS -g3 -ggdb)
elseif ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
    set(RUN_FLAGS -O1 -fno-tree-vectorize -ffast-math -funroll-loops -march=native)
    set(FAST_FLAGS -O2 -fno-tree-vectorize -ffast-math -funroll-loops -march=native)
    set(DEBUG_FLAGS -g3 -ggdb -Wno-deprecated)
    set(COVER_FLAGS -fprofile-arcs -ftest-coverage)
elseif ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Intel")
    add_compile_options(-no-parallel -mkl=sequential -wd1224,161)
    set(FAST_FLAGS -O2 -mdynamic-no-pic -funroll-loops -fno-math-errno -mavx)
    set(DEBUG_FLAGS -g -Wall -no-pie -wd279,383,810,869,981,1418,1419,1572,2259)
elseif ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "MSVC")
    message(FATAL_ERROR "Microsoft Visual Studio not supported for compilation")
else()
    message(FATAL_ERROR "Unrecognized compiler: ${CMAKE_CXX_COMPILER_ID}")
endif()


#file(COPY ${PROJECT_SOURCE_DIR}/cym DESTINATION ${PROJECT_BINARY_DIR})

add_compile_options(-Wno-deprecated-declarations)
add_compile_options(-shared -fPIC)
add_compile_options(-finline-functions)
add_compile_options(${FAST_FLAGS})
include_directories("../src" )


include_directories("../src/base")
include_directories("../src/math")
include_directories("../src/sim")

if (MAKE_PLAY)
    include_directories("../src/disp")
    include_directories("../src/gym")
    include_directories("../src/gym/deps")
    include_directories("../src/play")
endif()

if (MAKE_TOOLS)
    include_directories("../src/tools")
endif()

if (MAKE_TESTS)
    include_directories("../src/test")
endif()


set(SOURCES_BASE
    operator_new.cc
    signal_handlers.cc
    messages.cc
    filewrapper.cc
    filepath.cc
    iowrapper.cc
    exceptions.cc
    time_date.cc
    inventory.cc
    stream_func.cc
    tokenizer.cc
    glossary.cc
    property.cc
    property_list.cc
    backtrace.cc
    print_color.cc
)

list(TRANSFORM SOURCES_BASE PREPEND "${PROJECT_SOURCE_DIR}/../src/base/")

set(BASE_INCLUDES math base)
list(TRANSFORM BASE_INCLUDES PREPEND "${PROJECT_SOURCE_DIR}/../src/")

add_library(${BASE_LIBRARY} STATIC "${SOURCES_BASE}")
target_link_libraries(${BASE_LIBRARY} PUBLIC ${CURSES_LIBRARIES} )

set_source_files_properties(
    PROPERTIES
    EXTERNAL_OBJECT true
    GENERATED true
)

set(SOURCES_DISP
    view.cc
    view_prop.cc
    glapp.cc
    fiber_disp.cc
    line_disp.cc
    point_disp.cc
    grid_display.cc
    display_prop.cc
    display.cc
    display1.cc
    display2.cc
    display3.cc
 )

list(TRANSFORM SOURCES_DISP PREPEND "${PROJECT_SOURCE_DIR}/../src/disp/")

set(SOURCES_GYM
gle.cc
    gym_matrix.cc
    gym_cap.cc
    gym_view.cc
    gym_vect.cc
    gym_draw.cc
    gym_flute.cc
    gym_check.cc
    gym_menu.cc
    gym_zoo.cc
    gym_flat.cc
    gym_image.cc
    gym_color.cc
    gym_color_list.cc
    save_image.cc
    opengl.cc
    save_image_gl.cc
    offscreen.cc
    fg_font.cc
    fg_stroke.cc
)
list(TRANSFORM SOURCES_GYM PREPEND "${PROJECT_SOURCE_DIR}/../src/gym/")

set(SOURCES_GYM_DEPS
    spng.c
    miniz.c
)
list(TRANSFORM SOURCES_GYM_DEPS PREPEND "${PROJECT_SOURCE_DIR}/../src/gym/deps/")

set_property(SOURCE spng.c PROPERTY COMPILE_DEFINITIONS SPNG_STATIC SPNG_USE_MINIZ)


set(DISP_INCLUDES math base sim sim/organizers disp)
list(TRANSFORM DISP_INCLUDES PREPEND "${PROJECT_SOURCE_DIR}/../src/")

add_library(${DISP_LIBRARY} STATIC ${SOURCES_DISP} ${SOURCES_GYM} ${SOURCES_GYM_DEPS})
#add_library(${DISP_LIBRARY} STATIC ${SOURCES_DISP})

target_compile_definitions(${DISP_LIBRARY} PRIVATE -DDISPLAY)
target_include_directories(${DISP_LIBRARY} PUBLIC "${DISP_INCLUDES}" )


set(SOURCES_MATH
    vector1.cc
    vector2.cc
    vector3.cc
    vector4.cc
    matrix11.cc
    matrix22.cc
    matrix33.cc
    matrix34.cc
    rasterizer.cc
    sparmatsym1.cc
    sparmatsym2.cc
    sparmatsymblk.cc
    sparmatsymblkdiag.cc
    sparmatblk.cc
    matfull.cc
    polygon.cc
    spherical_code.cc
    random.cc
    modulo.cc 
    tesselator.cc
    random_vector.cc
    project_ellipse.cc
    SFMT.c
    random_seed.cc
    random_pcg.cc
)

list(TRANSFORM SOURCES_MATH PREPEND "${PROJECT_SOURCE_DIR}/../src/math/")

set(MATH_INCLUDES math base)
list(TRANSFORM MATH_INCLUDES PREPEND "${PROJECT_SOURCE_DIR}/../src/")

add_library(${MATH_LIBRARY} STATIC ${SOURCES_MATH})
target_include_directories(${MATH_LIBRARY} PUBLIC "${MATH_INCLUDES}" )

set(SOURCES_PLAY
    player_prop.cc
    player.cc
    play.cc
)

list(TRANSFORM SOURCES_PLAY PREPEND "${PROJECT_SOURCE_DIR}/../src/play/")

if(MAKE_PLAY)
    add_executable(${PLAY_TARGET} ${SOURCES_PLAY})

    target_link_libraries(${PLAY_TARGET} PUBLIC
        "${CURSES_LIBRARIES}"
        "${SIMG_LIBRARY}"
        "${DISP_LIBRARY}"
        "${GYM_LIBRARY}"
        "${MATH_LIBRARY}"
        "${BASE_LIBRARY}"
        "${OPENGL_LIBS}"
        "${LAPACK_BLAS}"
        Threads::Threads
        ZLIB::ZLIB
    )
    
    set(PLAY_INCLUDES math base sim gym disp)
    list(TRANSFORM PLAY_INCLUDES PREPEND "${PROJECT_SOURCE_DIR}/../src/")

    target_include_directories(${PLAY_TARGET} PUBLIC "${PLAY_INCLUDES}")
    target_include_directories(${PLAY_TARGET} PUBLIC "${DISP_INCLUDES}")
endif(MAKE_PLAY)


set(SOURCES_SIM
    mecable.cc meca.cc mecapoint.cc
    interpolation.cc interpolation4.cc
    fiber_segment.cc fiber_site.cc
    primitives.cc lattice.cc
    object.cc object_pool.cc object_set.cc
    sphere_prop.cc sphere.cc sphere_set.cc
    bead.cc bead_set.cc
    solid_prop.cc solid.cc solid_set.cc
    field.cc field_prop.cc field_set.cc
    event.cc event_set.cc
    chain.cc mecafil.cc
    fiber.cc fiber_prop.cc fiber_set.cc
    hand.cc hand_list.cc hand_prop.cc hand_monitor.cc
    single.cc single_prop.cc single_set.cc
    couple.cc couple_prop.cc couple_set.cc
    organizer.cc organizer_set.cc
    fiber_grid.cc point_grid.cc locus_grid.cc
    space.cc space_prop.cc space_set.cc
    simul.cc simul_prop.cc simul_part.cc
    interface.cc parser.cc
)

set(SOURCES_SPACES
    space_square.cc
    space_sphere.cc
    space_dice.cc
    space_torus.cc
    space_polygon.cc
    space_banana.cc
    space_ellipse.cc
    space_cylinder.cc
    space_cylinderZ.cc
    space_capsule.cc
    space_strip.cc
    space_periodic.cc
    space_cylinderP.cc
    space_bicylinder.cc
    space_dynamic_prop.cc
    space_dynamic_ellipse.cc
    space_dynamic_sphere.cc
    space_dynamic_disc.cc
    space_force.cc
    space_polygonZ.cc
    space_disc.cc
    space_lid.cc
    space_ring.cc
    space_mesh.cc
)
list(TRANSFORM SOURCES_SPACES PREPEND "spaces/")

set(SOURCES_HANDS
    motor.cc motor_prop.cc
    slider.cc slider_prop.cc
    actor.cc actor_prop.cc
    nucleator.cc nucleator_prop.cc
    tracker.cc tracker_prop.cc
    cutter.cc cutter_prop.cc
    rescuer.cc rescuer_prop.cc
    mighty.cc mighty_prop.cc
    chewer_prop.cc chewer.cc
    walker_prop.cc walker.cc
    regulator_prop.cc regulator.cc
    digit_prop.cc digit.cc
    myosin_prop.cc myosin.cc
    dynein_prop.cc dynein.cc
    kinesin_prop.cc kinesin.cc
)
list(TRANSFORM SOURCES_HANDS PREPEND "hands/")

set(SOURCES_FIBERS
    dynamic_fiber.cc dynamic_fiber_prop.cc
    classic_fiber.cc classic_fiber_prop.cc
    treadmilling_fiber.cc treadmilling_fiber_prop.cc
    growing_fiber.cc growing_fiber_prop.cc
)
list(TRANSFORM SOURCES_FIBERS PREPEND "fibers/")

set(SOURCES_SINGLES
    picket.cc picket_long.cc
    wrist.cc wrist_long.cc
)
list(TRANSFORM SOURCES_SINGLES PREPEND "singles/")

set(SOURCES_COUPLES
    couple_long.cc
    crosslink.cc crosslink_long.cc crosslink_prop.cc
    bridge.cc bridge_prop.cc
    shackle.cc shackle_long.cc shackle_prop.cc
    fork.cc fork_prop.cc
    duo.cc duo_prop.cc duo_long.cc
)
list(TRANSFORM SOURCES_COUPLES PREPEND "couples/")

set(SOURCES_ORGANIZERS
    aster.cc aster_prop.cc
    nucleus.cc nucleus_prop.cc
    fake.cc fake_prop.cc
    bundle.cc bundle_prop.cc
)
list(TRANSFORM SOURCES_ORGANIZERS PREPEND "organizers/")

set(SOURCES_READ
    frame_reader.cc
    sim_thread.cc
)

# objects containing graphical code under the DISPLAY keyword:
set(SOURCES_WITH_DISPLAY
    ${SOURCES_SPACES}
    space.cc
    field.cc
    fiber_grid.cc
    point_grid.cc
)

set(SOURCES_CYTOSIM
    "${SOURCES_SIM}"
    "${SOURCES_SPACES}"
    "${SOURCES_HANDS}"
    "${SOURCES_FIBERS}"
    "${SOURCES_SINGLES}"
    "${SOURCES_COUPLES}"
    "${SOURCES_ORGANIZERS}"
    "${SOURCES_READ}"
)

set(ALL_SIM_SRC_DIR sim sim/fibers sim/hands sim/singles sim/couples sim/organizers sim/spaces)


list(TRANSFORM SOURCES_CYTOSIM PREPEND "${PROJECT_SOURCE_DIR}/../src/sim/")
list(TRANSFORM SOURCES_WITH_DISPLAY PREPEND "${PROJECT_SOURCE_DIR}/../src/sim/")

set(SIM_INCLUDES math base sim "${ALL_SIM_SRC_DIR}")
list(TRANSFORM SIM_INCLUDES PREPEND "${PROJECT_SOURCE_DIR}/../src/")

add_library(${SIM_LIBRARY} STATIC ${SOURCES_CYTOSIM})
target_include_directories(${SIM_LIBRARY} PUBLIC "${SIM_INCLUDES}" )

if(MAKE_SIM)
    add_compile_options(-fPIC -shared -Wl,undefined,dynamic)
    add_executable(${SIM_TARGET} "${PROJECT_SOURCE_DIR}/../src/sim/sim.cc")
    include_directories(PUBLIC "${SIM_INCLUDES}" )
    target_link_libraries(${SIM_TARGET} PRIVATE
        "${SIM_LIBRARY}"
        "${MATH_LIBRARY}"
        "${BASE_LIBRARY}"
        "${LAPACK_BLAS}"
        Threads::Threads
    )
endif(MAKE_SIM)


if(MAKE_PLAY)

    set(SIMG_INCLUDES math base sim sim/organizers disp)
    list(TRANSFORM SIMG_INCLUDES PREPEND "${PROJECT_SOURCE_DIR}/../src/")

    #set(SOURCES_CYTOSIM_NO_DISPLAY ${SOURCES_CYTOSIM})
    #list(REMOVE_ITEM SOURCES_CYTOSIM_NO_DISPLAY ${SOURCES_WITH_DISPLAY})

    add_library(${SIMG_LIBRARY} STATIC ${SOURCES_CYTOSIM})
    target_include_directories(${SIMG_LIBRARY} PUBLIC "${SIMG_INCLUDES}")

    # It is only necessary to compile files in ${SOURCES_WITH_DISPLAY} with this flag
    # but I do not know how to specify this with CMake
    # Hence by setting a target_compile_definitions, all source will be compiled with -DDISPLAY

    target_compile_definitions(${SIMG_LIBRARY} PRIVATE DISPLAY)

    # This below does not work, as it sets the compile options for all targets including the files

    foreach(FILE ${SOURCES_WITH_DISPLAY})
        #set_source_files_properties(${FILE} TARGET_DIRECTORY ${SIMG_LIBRARY} PROPERTIES COMPILE_DEFINITIONS "DISPLAY")
        #message(${FILE} "will be compiled with -DDISPLAY")
    endforeach()

endif(MAKE_PLAY)

############# PYCYTOSIM SPECIFIC #############

set(TOOL_INCLUDES math base sim play cpython)
list(TRANSFORM TOOL_INCLUDES PREPEND "${PROJECT_SOURCE_DIR}/../src/")
find_package(Python3 COMPONENTS Interpreter Development)
find_package(pybind11 CONFIG)
find_package(Curses REQUIRED)
include_directories(${CURSES_INCLUDE_DIR})

set(TOOL_LIBS
    "${SIM_LIBRARY}"
    "${MATH_LIBRARY}"
    "${BASE_LIBRARY}"
    "${LAPACK_BLAS}"
    Threads::Threads
)

#Sources 
set(PYCY_SOURCES
    "${PROJECT_SOURCE_DIR}/../src/cpython/pycytosim.cc"
)
set(PYPL_SOURCES
    "${PROJECT_SOURCE_DIR}/../src/cpython/pycytoplay.cc"
)

set_source_files_properties(
        PROPERTIES
        EXTERNAL_OBJECT true
        GENERATED true
)


# Module cytosim and compile options
pybind11_add_module(${PYSIM_LIBRARY_NAME}  ${PYCY_SOURCES})
add_compile_options(-fPIC -shared -Wl,undefined,dynamic_lookup)
target_link_libraries(${PYSIM_LIBRARY_NAME} PUBLIC "${TOOL_LIBS}")
target_include_directories(${PYSIM_LIBRARY_NAME} PUBLIC ${TOOL_INCLUDES})
target_include_directories(${PYSIM_LIBRARY_NAME} PUBLIC "${SIM_INCLUDES}" )


# We need the libraries for pycytosim
include_directories(PUBLIC "${SIM_INCLUDES}" )
target_link_libraries(${PYSIM_LIBRARY_NAME} PRIVATE
    "${SIM_LIBRARY}"
    "${MATH_LIBRARY}"
    "${BASE_LIBRARY}"
    "${LAPACK_BLAS}"
    Threads::Threads
)

# Making sure it's the good name ; can be modified to add location 
set_target_properties(${PYSIM_LIBRARY_NAME} PROPERTIES OUTPUT_NAME "${PYSIM_LIBRARY_NAME}")


if(MAKE_PLAY)
    #Testing stuff 
    set(PLAY_LIBS play_lib)
    target_compile_definitions(${SIMG_LIBRARY} PRIVATE DISPLAY)
    add_library(${PLAY_LIBS} STATIC ${SOURCES_PLAY})
    target_include_directories(${PLAY_LIBS} PUBLIC "${PLAY_INCLUDES}")

    pybind11_add_module(${PYPLAY_LIBRARY_NAME}  ${PYPL_SOURCES})
    target_compile_definitions(${PYPLAY_LIBRARY_NAME} PRIVATE DISPLAY)
    target_link_libraries(${PYPLAY_LIBRARY_NAME} PUBLIC "${TOOL_LIBS}")
    target_link_libraries(${PYPLAY_LIBRARY_NAME} PRIVATE "${PLAY_LIBS}")
    target_include_directories(${PYPLAY_LIBRARY_NAME} PUBLIC ${TOOL_INCLUDES})
    target_include_directories(${PYPLAY_LIBRARY_NAME} PUBLIC "${SIM_INCLUDES}" )
    target_include_directories(${PYPLAY_LIBRARY_NAME} PUBLIC "${PLAY_INCLUDES}" )
    target_link_libraries(${PYPLAY_LIBRARY_NAME} PUBLIC
        "${SIMG_LIBRARY}"
        "${DISP_LIBRARY}"
        "${GYM_LIBRARY}"
        "${MATH_LIBRARY}"
        "${BASE_LIBRARY}"
        "${OPENGL_LIBS}"
        "${LAPACK_BLAS}"
        Threads::Threads
        ZLIB::ZLIB
    )

    set_target_properties(${PYPLAY_LIBRARY_NAME} PROPERTIES OUTPUT_NAME "${PYPLAY_LIBRARY_NAME}")
endif(MAKE_PLAY)    





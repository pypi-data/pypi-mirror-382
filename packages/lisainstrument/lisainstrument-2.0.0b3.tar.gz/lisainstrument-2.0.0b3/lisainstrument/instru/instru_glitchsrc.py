"""Functions for setting up glitch source according to Instrument parameter


The init_glitch_source function creates the glitch source used in the simulator
"""

import logging

from lisainstrument.glitches import (
    GlitchSource,
    GlitchSourceSplines,
    GlitchSourceZero,
    glitch_file,
)


def init_glitch_source(
    glitches: str | None, tmin: float, tmax: float
) -> tuple[GlitchSource, str | None]:
    """Parse glitches parameter and set up corresponding GlitchSource

    Args:
        glitches: path of glitch file or None for no glitches
        tmin: Start of time interval that needs to be be covered
        tmax: End of time interval that needs to be be covered

    Returns:
        Glitch source, glitch file name or None

    """
    logger = logging.getLogger(__name__)

    res_glitch_src: GlitchSource
    res_glitch_file: str | None

    match glitches:
        case None:
            res_glitch_file = None
            logger.info("Not adding any glitches")
            res_glitch_src = GlitchSourceZero()
        case str(glitch_path):
            res_glitch_file = glitch_path
            logger.info(
                "Interpolating glitch signals from glitch file '%s'", glitch_path
            )
            glf = glitch_file(glitch_path)
            logger.debug("Using glitch file version %s", glf.format_version)
            if glf.format_version.is_devrelease or glf.format_version.local is not None:
                logger.warning("You are using a glitch file in a development version")
            res_glitch_src = GlitchSourceSplines(
                glf,
                # ~ self.t0, self.t0 + self.physics_dt * self.physics_size
                tmin,
                tmax,
            )
        case _:
            msg = f"invalid value '{glitches}' for glitches"
            raise RuntimeError(msg)

    return res_glitch_src, res_glitch_file

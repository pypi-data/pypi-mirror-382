import argparse
from dorn.app import Gui


def main():
    """Command-line interface for GUI program"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        nargs=3,
        metavar=("THERAPY_NAME", "RADIONUCLIDE", "INPATIENT"),
        dest="therapy_measured",
        help="""
        add a therapy option with measured clearance data. Use double quotes.
        E.g. -m "Y-90-dotatate skin cancer" Y-90 1
        """,
    )
    parser.add_argument(
        "-g",
        nargs=5,
        metavar=(
            "THERAPY_NAME",
            "RADIONUCLIDE",
            "INPATIENT",
            "MODEL",
            "MODEL_PARAMETERS",
        ),
        dest="therapy_generic",
        help="""
        add a therapy option with a generic clearance function. Use double quotes.
        MODEL_PARAMETERS is
        "dose_rate_1m_init_perA0(uSv/h/MBq) effective_half_life(h)" for MODEL exponential and
        "dose_rate_1m_init_perA0(uSv/h/MBq) fraction_1[0-1] half_life_1(h) half_life_2(h)" for MODEL biexponential.
        E.g. -g "Lu-177-PSMA (generic clearance)" Lu-177 0 exponential "0.05 20"
        """,
    )
    parser.add_argument(
        "-i",
        action="store_true",
        dest="write_info",
        help="write info on radionuclide and therapy options to csv files and quit",
    )
    args = parser.parse_args()

    add_therapy_measured = None
    if args.therapy_measured is not None:
        # if more than 1, takes the last
        therapy_name, radionuclide, inpatient = args.therapy_measured
        if inpatient not in ["0", "1"]:
            raise ValueError("INPATIENT is 0 (False) or 1 (True)")
        inpatient = bool(int(inpatient))
        add_therapy_measured = [therapy_name, radionuclide, inpatient]

    add_therapy_generic = None
    if args.therapy_generic is not None:
        # if more than 1, takes the last
        (
            therapy_name,
            radionuclide,
            inpatient,
            model,
            meaningful_parameters,
        ) = args.therapy_generic
        if inpatient not in ["0", "1"]:
            raise ValueError("INPATIENT is 0 (False) or 1 (True)")
        inpatient = bool(int(inpatient))
        meaningful_parameters = meaningful_parameters.split()
        for x in meaningful_parameters:
            try:
                float(x)
            except Exception as e:
                raise ValueError(f"Model parameters must be numbers\n{e}")
        meaningful_parameters = [float(x) for x in meaningful_parameters]
        add_therapy_generic = [
            therapy_name,
            radionuclide,
            inpatient,
            model,
            meaningful_parameters,
        ]

    Gui(
        add_therapy_measured=add_therapy_measured,
        add_therapy_generic=add_therapy_generic,
        write_info=args.write_info,
    )


if __name__ == "__main__":
    main()

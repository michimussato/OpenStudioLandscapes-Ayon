import textwrap

import snakemd


def readme_feature(doc: snakemd.Document) -> snakemd.Document:

    # Some Specific information

    doc.add_heading(
        text="Official Resources",
        level=1,
    )

    # Logo

    doc.add_paragraph(
        snakemd.Inline(
            text=textwrap.dedent(
                """\
                Logo Ayon\
                """
            ),
            image={
                "Ayon": "https://ynput.io/wp-content/uploads/2023/04/ayon-whiteg-dot.svg",
            }["Ayon"],
            link="https://ynput.io/ayon/",
        ).__str__()
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            """\
            Ayon is written and maintained by Ynput, a company based
            in Czech Republic:\
            """
        )
    )

    # Logo

    doc.add_paragraph(
        snakemd.Inline(
            text=textwrap.dedent(
                """\
                Logo Ynput\
                """
            ),
            image={
                "Ynput": "https://ynput.io/wp-content/uploads/2022/09/ynput-logo-small-bg.svg",
            }["Ynput"],
            link="https://ynput.io",
        ).__str__()
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            """\
            Ynput offers different versions of Ayon\
            """
        )
    )

    doc.add_unordered_list(
        [
            "Community",
            "Pro Cloud",
            "Studio Cloud",
        ]
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            """\
            `OpenStudioLandscapes-Ayon` is based on the [Community](https://ynput.io/ayon/pricing/)
            version provided by their own Docker image:\
            """
        )
    )

    doc.add_unordered_list(
        [
            "[https://github.com/ynput/ayon-docker](https://github.com/ynput/ayon-docker)",
        ]
    )

    doc.add_heading(
        text="Official Documentation",
        level=2,
    )

    doc.add_unordered_list(
        [
            "[Features](https://docs.ayon.dev/features)",
            "[User Docs](https://docs.ayon.dev/docs/artist_getting_started)",
            "[Admin Docs](https://docs.ayon.dev/docs/system_introduction)",
            "[Dev Docs](https://docs.ayon.dev/docs/dev_introduction)",
        ]
    )

    doc.add_heading(
        text="Dev Resources",
        level=3,
    )

    doc.add_unordered_list(
        [
            "[REST API Docs](https://docs.ayon.dev/api)",
            "[GraphQL API Explorer](https://playground.ayon.app/explorer)",
            "[Python API Docs](https://docs.ayon.dev/ayon-python-api)",
            "[C++ API Docs](https://docs.ayon.dev/ayon-cpp-api)",
            "[USD Resolver Docs](https://docs.ayon.dev/ayon-usd-resolver)",
            "[Frontend React Components](https://components.ayon.dev)",
        ]
    )

    return doc


if __name__ == "__main__":
    pass

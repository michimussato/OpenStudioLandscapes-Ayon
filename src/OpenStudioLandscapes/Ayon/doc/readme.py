import textwrap

import snakemd


def readme_feature(
    doc: snakemd.Document,
    main_header: str,
) -> snakemd.Document:

    # Some Specific information

    doc.add_heading(
        text="Initial OpenStudioLandscapes-Ayon Server Setup",
        level=2,
    )

    doc.add_paragraph(text=textwrap.dedent("""\
            The freshly deployed `OpenStudioLandscapes-Ayon` instance 
            does **not** come with pre-created users. Ayon suggests
            to run `make setup`, however, this does not seem 
            to work reliably. Execute the command 
            (locally) shown here for this matter when 
            the Landscape is running:\
            """))

    doc.add_paragraph(
        snakemd.Inline(
            text=textwrap.dedent("""\
                Screenshot\
                """),
            image="media/images/2026-06-05_12-22.png",
            # link="https://ynput.io",
        ).__str__()
    )

    doc.add_paragraph(
        snakemd.Inline(
            text=textwrap.dedent("""\
                Screenshot\
                """),
            image="media/images/2026-06-05_12-22_1.png",
            # link="https://ynput.io",
        ).__str__()
    )

    doc.add_paragraph(
        snakemd.Inline(
            text=textwrap.dedent("""\
                Screenshot\
                """),
            image="media/images/2026-06-05_12-02.png",
            # link="https://ynput.io",
        ).__str__()
    )

    doc.add_code(
        code=textwrap.dedent("""\
            # $(which docker) \\
                --config /home/michael/test/.landscapes/2026-06-05_10-22-38__small-quartz-rambunctious-cephalopod/OpenStudioLandscapes/OpenStudioLandscapes_Base__docker_config_json \\
                compose \\
                --project-name 2026-06-05_10-22-38__small-quartz-rambunctious-cephalopod-default \\
                exec \\
                --no-tty \\
                server \\
                python -m setup - < /home/michael/test/.landscapes/2026-06-05_10-22-38__small-quartz-rambunctious-cephalopod/OpenStudioLandscapes-Ayon/settings/setup_template.json
            INFO    __main__                   | Starting setup
            DEBUG   setup.database             | Applying 12 database migrations
            INFO    setup.template             | Force install requested
            INFO    setup.template             | Reading setup file from stdin
            DEBUG   setup.users                | Creating password for user openstudiolandscapes
            INFO    setup.users                | Saving user openstudiolandscapes
            SUCCESS __main__                   | Setup is finished\
            """),
        lang="generic",
    )

    doc.add_paragraph(text=textwrap.dedent("""\
            After this step, you should be able to log in to Ayon with the credentials 
            specified in the `setup_template.json` file. Consult `config.yml` for the defaults.\
            """))

    doc.add_paragraph(
        snakemd.Inline(
            text=textwrap.dedent("""\
                Screenshot\
                """),
            image="media/images/2026-06-05_12-23.png",
            # link="https://ynput.io",
        ).__str__()
    )

    doc.add_paragraph(text=textwrap.dedent("""\
            More information here:\
            """))

    doc.add_unordered_list(
        [
            "[AYON Server Local Deployment](https://help.ayon.app/en/help/articles/2293963-ayon-server-local-deployment)",
            "[AYON Server Provisioning](https://help.ayon.app/en/articles/4089565-ayon-server-provisioning)",
            "[template.json](https://github.com/ynput/ayon-docker/blob/main/settings/template.json)",
        ]
    )

    doc.add_horizontal_rule()

    doc.add_heading(
        text=main_header,
        level=1,
    )

    # Logo

    doc.add_paragraph(
        snakemd.Inline(
            text=textwrap.dedent("""\
                Logo Ayon\
                """),
            image={
                "Ayon": "https://ynput.io/wp-content/uploads/2023/04/ayon-whiteg-dot.svg",
            }["Ayon"],
            link="https://ynput.io/ayon/",
        ).__str__()
    )

    doc.add_paragraph(text=textwrap.dedent("""\
            Ayon is written and maintained by Ynput, a company based
            in Czech Republic:\
            """))

    # Logo

    doc.add_paragraph(
        snakemd.Inline(
            text=textwrap.dedent("""\
                Logo Ynput\
                """),
            image={
                "Ynput": "https://ynput.io/wp-content/uploads/2022/09/ynput-logo-small-bg.svg",
            }["Ynput"],
            link="https://ynput.io",
        ).__str__()
    )

    doc.add_paragraph(text=textwrap.dedent("""\
            Ynput offers different versions of Ayon\
            """))

    doc.add_unordered_list(
        [
            "Community",
            "Pro Cloud",
            "Studio Cloud",
        ]
    )

    doc.add_paragraph(text=textwrap.dedent("""\
            `OpenStudioLandscapes-Ayon` is based on the [Community](https://ynput.io/ayon/pricing/)
            version provided by their own Docker image:\
            """))

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

    doc.add_horizontal_rule()

    return doc


if __name__ == "__main__":
    pass

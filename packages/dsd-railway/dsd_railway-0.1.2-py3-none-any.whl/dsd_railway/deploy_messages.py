"""A collection of messages used during the configuration and deployment process."""

# For conventions, see documentation in core deploy_messages.py

from textwrap import dedent

from django.conf import settings


confirm_automate_all = """
The --automate-all flag means django-simple-deploy will:
- ...
- Commit all changes to your project that are necessary for deployment.
- Push these changes to Railway.
- Open your deployed project in a new browser tab.
"""

cancel_railway = """
Okay, cancelling Railway configuration and deployment.
"""

# DEV: This could be moved to deploy_messages, with an arg for platform and URL.
cli_not_installed = """
In order to deploy to Railway, you need to install the Railway CLI.
  See here: ...
After installing the CLI, you can run the deploy command again.
"""

cli_logged_out = """
You are currently logged out of the Railway CLI. Please log in,
  and then run the deploy command again.
You can log in from  the command line:
  $ ...
"""


# --- Dynamic strings ---
# These need to be generated in functions, to display information that's determined as
# the script runs.

def success_msg(log_output=""):
    """Success message, for configuration-only run.

    Note: This is immensely helpful; I use it just about every time I do a
      manual test run.
    """

    msg = dedent(
        f"""
        --- Your project is now configured for deployment on Railway ---

        To deploy your project, you will need to:
        - Commit the changes made in the configuration process.
            $ git status
            $ git add .
            $ git commit -am "Configured project for deployment."
        - Push your project to Railway's servers:
            $ ...
        - Open your project:
            $ ...    
        - As you develop your project further:
            - Make local changes
            - Commit your local changes
            - Run `...` again to push your changes.
    """
    )

    if log_output:
        msg += dedent(
            f"""
        - You can find a full record of this configuration in the dsd_logs directory.
        """
        )

    return msg


def success_msg_automate_all(deployed_url, project_id):
    """Success message, when using --automate-all."""

    msg = dedent(
        f"""

        --- Your project should now be deployed on Railway ---

        It should have opened up in a new browser tab. If you see a
          "server not available" message, wait a minute or two and
          refresh the tab. It sometimes takes a few minutes for the
          server to be ready.
        - You can also visit your project at {deployed_url}
        - Project ID: {project_id}

        If you make further changes and want to push them to Railway,
        commit your changes and then run `...`.
    """
    )
    return msg

from kabaret import flow
from libreflow.flows.default.flow.shot import CreateKitsuShots, Sequence


class SKCreateKitsuShots(CreateKitsuShots):
    """Add digits to shots when creating shots."""

    def __init__(self, parent, name):
        """Initialize based on CreateKitsuShots."""
        super(SKCreateKitsuShots, self).__init__(parent, name)

    def add_shot_digit(self, name):
        """Add digit into shot code.

        Args:
            name (str): name of the shot (p000)

        """
        if not self._sequence.shots[name].code.get():
            shot_digit = name.replace("p", "")
            self._sequence.shots[name].code.set(shot_digit)

    def run(self, button):
        """Execute the render action.

        Args:
            button (str): The label of the button pressed by the user (e.g., 'Create Shots' or 'Cancel').

        Returns:
            Any: the result of the parent run method if executed, or None if canceled.

        """
        if button == "Cancel":
            return

        session = self.root().session()

        project_type = self.root().project().kitsu_config().project_type.get()

        skip_existing = self.skip_existing.get()
        shots_data = (
            self.root()
            .project()
            .kitsu_api()
            .get_shots_data(
                self._sequence.name(),
                episode_name=self._film.name() if project_type == "tvshow" else None,
            )
        )
        for data in shots_data:
            name = data["name"]

            if not self._sequence.shots.has_mapped_name(name):
                session.log_info(f"[Create Kitsu Shots] Creating Shot {name}")
                s = self._sequence.shots.add(name)
                self.add_shot_digit(name)
            elif not skip_existing:
                s = self._sequence.shots[name]
                session.log_info(f"[Create Kitsu Shots] Updating Default Tasks {name}")
                s.ensure_tasks()
            else:
                self.add_shot_digit(name)
                continue

            if not self._sequence.shots[name].code.get():
                shot_digit = name.replace("sh", "")
                self._sequence.shots[name].code.set(shot_digit)

            if self.create_task_default_files.get():
                for t in s.tasks.mapped_items():
                    session.log_info(
                        f"[Create Kitsu Shots] Updating Default Files {name} {t.name()}"
                    )
                    t.create_dft_files.files.update()
                    t.create_dft_files.run(None)

        self._sequence.shots.touch()


def sk_create_kitsu_shots(parent):
    if isinstance(parent, Sequence):
        r = flow.Child(SKCreateKitsuShots)
        r.name = "create_shots"
        r.index = 25
        return r
    return None


def install_extensions(session):
    return {
        "sk": [
            sk_create_kitsu_shots,
        ]
    }


from . import _version

__version__ = _version.get_versions()["version"]

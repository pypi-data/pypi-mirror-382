"""
This package provides utilities for generating synthetic dialogues using instruction-tuned large language models (LLMs).
Dialogues are generated primarily via role-playing, where each agent is defined by a Persona object. The package
supports dialogue orchestration, context management, and flexible serialization for downstream tasks.

Main components:

    - Dialog, Turn, Event: Data structures for representing dialogues and their events.
    - Context, Persona and Agent: For defining and simulating role-played agents in a given context.
    - Orchestrators: For controlling agent behavior during dialogue generation.
    - Evaluation: Utilities and metrics for assessing dialogue quality (coherence, turn balance, persona/goal
      adherence, safety screening, lexical/statistical reports) and for building reproducible evaluation pipelines.
    - Interpretability: Layer/token-level activation capture, inspection (Inspector, hooks), steering (directional
      modulation of representations), and instruction extraction utilities (see interpretability.py).
"""
# SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Sergio Burdisso <sergio.burdisso@idiap.ch>
# SPDX-License-Identifier: MIT
import os
import re
import json
import csv
import logging
import importlib

from tqdm.auto import tqdm
from pydantic import BaseModel, Field
from print_color import print as cprint
from typing import List, Union, Optional, Any, Pattern, Dict

from .base import BaseAttributeModel
from .util import __version__, make_serializable, get_timestamp, remove_newlines, get_universal_id, _get_dynamic_version

__version__ = __version__

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s:%(name)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# import config sumbodule as "config" attribute of the package
config = importlib.import_module("sdialog.config")


class Turn(BaseModel):
    """
    Represents a single turn in a dialogue.

    :param speaker: The name or role of the speaker.
    :type speaker: Optional[str]
    :param text: The utterance text for this turn.
    :type text: str
    """
    speaker: Optional[str] = None
    text: str

    def __len__(self):
        """
        Returns the number of words in the turn's text.

        :return: Number of words in the text.
        :rtype: int
        """
        return len(self.text.split())

    def __str__(self):
        return f"{self.speaker}: {self.text}"

    def prompt(self) -> str:
        """Generates a prompt string for this turn."""
        return json.dumps(self.model_dump(), indent=2)

    def print(self):
        cprint(self.text, tag=self.speaker, tag_color="blue", color="white")


class Event(BaseModel):
    """
    Represents an event in a dialogue, which may be an utterance, instruction, or other action.

    :param agent: The agent responsible for the event (e.g., "user", "system").
    :type agent: Optional[str]
    :param action: The type of event (e.g., "utter", "instruct").
    :type action: str
    :param actionLabel: A label describing the action (e.g., type of instruction).
    :type actionLabel: Optional[str]
    :param content: The content of the event.
    :type content: Union[str, Dict, List]
    :param timestamp: The Unix timestamp of the event.
    :type timestamp: int
    """
    agent: Optional[str] = None  # "user", "system"
    action: str  # "utter", "instruct"
    actionLabel: Optional[str] = None  # action label (e.g. type of instruct)
    content: Union[str, Dict, List]  # the content of the event
    timestamp: int  # timestamp

    def model_post_init(self, context: Any, /) -> None:
        """
        Post-initialization hook (pydantic v2).
        Logs the event at DEBUG level after model validation / creation.

        :param context: Internal pydantic context (unused).
        :type context: Any

        :meta private:
        """
        logger.log(level=logging.DEBUG, msg=f"Event: {self}")


class Dialog(BaseModel):
    """
    A pydantic model representing a conversational dialogue with rich metadata,
    container-like access to turns, text utilities, analytics, and I/O helpers.

    :param version: Version of the dialogue format.
    :type version: Optional[str]
    :param timestamp: Timestamp of dialogue creation.
    :type timestamp: Optional[str]
    :param model: The model used to generate the dialogue.
    :type model: Optional[Union[str, Dict]]
    :param seed: The random seed used for generation.
    :type seed: Optional[int]
    :param id: Unique ID for the dialogue.
    :type id: Optional[Union[int, str]]
    :param parentId: ID of the parent dialogue, if any.
    :type parentId: Optional[Union[int, str]]
    :param complete: Whether the dialogue is complete.
    :type complete: Optional[bool]
    :param personas: Any is a subclass of MetaPersona.
    :type personas: Optional[dict[str, Any]]
    :param context: Shared context for the dialogue.
    :type context: Optional[Union[str, dict[str, Any]]]
    :param scenario: Scenario description or metadata.
    :type scenario: Optional[Union[dict, str]]
    :param turns: List of dialogue turns.
    :type turns: Optional[List[Turn]]
    :param events: List of dialogue events (optional).
    :type events: Optional[List[Event]]
    :param notes: Free-text notes or comments about the dialogue.
    :type notes: Optional[str]
    """
    version: Optional[str] = Field(default_factory=_get_dynamic_version)
    timestamp: Optional[str] = Field(default_factory=get_timestamp)
    model: Optional[Union[str, Dict]] = None
    seed: Optional[int] = None
    id: Optional[Union[int, str]] = Field(default_factory=get_universal_id)
    parentId: Optional[Union[int, str]] = None
    complete: Optional[bool] = None
    personas: Optional[dict[str, Any]] = None
    context: Optional[Union[str, dict[str, Any]]] = None
    scenario: Optional[Union[dict, str]] = None
    turns: Optional[List[Turn]] = Field(default_factory=list)
    events: Optional[List[Event]] = None
    notes: Optional[str] = None

    _path: Optional[str] = None

    def __len__(self):
        """
        Returns the number of turns in the dialogue.

        :return: Number of turns.
        :rtype: int
        """
        return len(self.turns)

    def __getitem__(self, index: Union[int, slice]) -> Union[Turn, "Dialog"]:
        """
        Allows indexing to retrieve a specific turn by its index or a range of turns.

        :param index: The index or slice of the turns to retrieve.
        :type index: Union[int, slice]
        :return: The turn at the specified index or a new Dialog with the selected range of turns.
        :rtype: Union[Turn, Dialog]
        """
        if isinstance(index, int):
            return self.turns[index]
        elif isinstance(index, slice):
            cloned_dialog = self.clone()
            cloned_dialog.turns = self.turns[index]
            return cloned_dialog
        else:
            raise TypeError("Index must be an integer or a slice.")

    def __iter__(self):
        """
        Allows iteration over the turns in the dialogue.

        :return: An iterator over the turns.
        :rtype: Iterator[Turn]
        """
        return iter(self.turns)

    def _transform_texts(self, fn, in_place: bool):
        """
        Internal utility: apply the string transformation function fn to each turn's text.

        :param fn: Callable transforming a str into a str.
        :type fn: Callable[[str], str]
        :param in_place: If True mutate this Dialog, otherwise work on a cloned copy.
        :type in_place: bool
        :return: The mutated (in_place=True) or cloned (in_place=False) Dialog.
        :rtype: Dialog
        """
        target = self if in_place else self.clone()
        for turn in target.turns:
            if turn.text is not None:
                turn.text = fn(turn.text)
        return target

    def lower(self, in_place: bool = True) -> "Dialog":
        """
        Apply str.lower() to every turn's text.

        :param in_place: If True modify this Dialog in place; otherwise return a cloned transformed Dialog.
        :type in_place: bool
        :return: The modified (or cloned) Dialog.
        :rtype: Dialog
        """
        return self._transform_texts(lambda s: s.lower(), in_place)

    def upper(self, in_place: bool = True) -> "Dialog":
        """
        Apply str.upper() to every turn's text.

        :param in_place: If True modify this Dialog in place; otherwise return a cloned transformed Dialog.
        :type in_place: bool
        :return: The modified (or cloned) Dialog.
        :rtype: Dialog
        """
        return self._transform_texts(lambda s: s.upper(), in_place)

    def title(self, in_place: bool = True) -> "Dialog":
        """
        Apply str.title() to every turn's text.

        :param in_place: If True modify this Dialog in place; otherwise return a cloned transformed Dialog.
        :type in_place: bool
        :return: The modified (or cloned) Dialog.
        :rtype: Dialog
        """
        return self._transform_texts(lambda s: s.title(), in_place)

    def capitalize(self, in_place: bool = True) -> "Dialog":
        """
        Apply str.capitalize() to every turn's text.

        :param in_place: If True modify this Dialog in place; otherwise return a cloned transformed Dialog.
        :type in_place: bool
        :return: The modified (or cloned) Dialog.
        :rtype: Dialog
        """
        return self._transform_texts(lambda s: s.capitalize(), in_place)

    def strip(self, chars: str = None, in_place: bool = True) -> "Dialog":
        """
        Apply str.strip(chars) to every turn's text.

        :param chars: Characters to strip; if None, default whitespace is stripped.
        :type chars: Optional[str]
        :param in_place: If True modify this Dialog in place; otherwise return a cloned transformed Dialog.
        :type in_place: bool
        :return: The modified (or cloned) Dialog.
        :rtype: Dialog
        """
        return self._transform_texts(lambda s: s.strip(chars) if chars is not None else s.strip(), in_place)

    def replace(self, old: str, new: str, count: int = -1, in_place: bool = True) -> "Dialog":
        """
        Apply str.replace(old, new, count) to every turn's text.
        If count < 0 all occurrences are replaced.

        :param old: Substring to be replaced.
        :type old: str
        :param new: Replacement substring.
        :type new: str
        :param count: Maximum number of replacements per text; if < 0 replace all.
        :type count: int
        :param in_place: If True modify this Dialog in place; otherwise return a cloned transformed Dialog.
        :type in_place: bool
        :return: The modified (or cloned) Dialog.
        :rtype: Dialog
        """
        return self._transform_texts(
            (lambda s: s.replace(old, new, count if count >= 0 else s.count(old))) if count >= 0
            else (lambda s: s.replace(old, new)),
            in_place
        )

    def re_sub(self,
               pattern: Union[str, Pattern],
               repl: Union[str, callable],
               count: int = 0,
               flags: int = 0,
               in_place: bool = True) -> "Dialog":
        """
        Apply re.sub(pattern, repl, text, count=count, flags=flags) to every turn's text.
        If pattern is a compiled regex, flags are ignored.

        :param pattern: Regex pattern (string or compiled).
        :type pattern: Union[str, Pattern]
        :param repl: Replacement string or callable.
        :type repl: Union[str, Callable]
        :param count: Max substitutions per text (0 means unlimited).
        :type count: int
        :param flags: Regex flags (ignored if compiled pattern provided).
        :type flags: int
        :param in_place: Mutate this Dialog if True; else return a cloned transformed Dialog.
        :type in_place: bool
        :return: The modified (or cloned) Dialog.
        :rtype: Dialog
        """
        return self._transform_texts(
            (lambda s: pattern.sub(repl, s, count=count)) if isinstance(pattern, re.Pattern)
            else (lambda s: re.sub(pattern, repl, s, count=count, flags=flags)),
            in_place
        )

    def length(self, mode: str = "words", words_per_minute: int = 130) -> int:
        """
        Returns the length of the dialogue according to the specified mode (number of words by default).

        :param mode: The mode for measuring length. Options:

            - ``"turns"``: Number of turns (default)
            - ``"words"``: Total number of words in all turns
            - ``"minutes"`` / ``"time"``: Approximate duration in minutes (``words_per_minute``/minute)
        :type mode: str
        :param words_per_minute: Words per minute for "minutes" mode (default is 130, which is a common estimate).
        :type words_per_minute: int
        :return: The computed length according to the mode.
        :rtype: int
        :raises ValueError: If an unknown mode is specified.
        """
        mode = mode.lower()
        if mode == "turns":
            return len(self.turns)
        elif mode == "words":
            return sum(len(turn.text.split()) for turn in self.turns)
        elif mode in ["minutes", "time"]:
            total_words = sum(len(turn.text.split()) for turn in self.turns)
            return max(1, int(round(total_words / words_per_minute)))
        else:
            raise ValueError(f"Unknown mode for `Dialog.length()`: {mode}")

    def clone(self, new_id: int = None) -> "Dialog":
        """
        Creates a deep copy of the dialogue.

        :param new_id: Optional ID to assign to the cloned dialog. If None, a new universal ID is generated.
        :type new_id: int, optional
        :return: A new Dialog object that is a deep copy of this one, with updated id and parentId.
        :rtype: Dialog
        """
        cloned = Dialog.from_dict(self.json())
        cloned.parentId = cloned.id
        cloned.id = new_id if new_id is not None else get_universal_id()

        return cloned

    def description(self, turn_template: str = None):
        """
        Returns a human-readable string representation of the dialogue.

        :param turn_template: Template for formatting each turn (default "{speaker}: {text}").
        :type turn_template: str
        :return: The formatted dialogue.
        :rtype: str
        """
        if turn_template is None:
            return "\n".join(f"{turn.speaker}: " + turn.text.replace('\n', ' ') if turn.speaker else turn.text
                             for turn in self.turns)

        return "\n".join(turn_template.format(speaker="" if turn.speaker is None else turn.speaker,
                                              text=turn.text.replace("\n", " "))
                         for turn in self.turns)

    def prompt(self) -> str:
        """Generates a prompt string for the entire dialogue."""
        return self.json(string=True)

    def json(self, string: bool = False, indent: int = 2):
        """
        Serializes the dialogue to JSON.

        :param string: If True, returns a JSON string; otherwise, returns a dict.
        :type string: bool
        :param indent: Indentation level for pretty-printing.
        :type indent: int
        :return: The serialized dialogue.
        :rtype: Union[str, dict]
        """
        data = self.model_dump()
        make_serializable(data)
        return json.dumps(data, indent=indent) if string else data

    def print(self, *a, **kw):
        """
        Pretty-prints a dialogue to the console, with optional scenario and orchestration details.

        :param scenario: If True, prints scenario information.
        :type scenario: bool
        :param orchestration: If True, prints also orchestration events.
        :type orchestration: bool
        :param think: If True, prints "thinking" events.
        :type think: bool
        :param all: If True, prints all types of events.
        :type all: bool
        """
        _print_dialog(self, *a, **kw)

    def to_file(self, path: str = None, type: str = "auto", makedir: bool = True, overwrite: bool = True):
        """
        Saves the dialogue to a file in JSON, CSV, or plain text format.

        :param path: Output file path, if not provided, uses the same path used to load the dialogue.
        :type path: str
        :param type: "json", "csv", "txt", or "auto" (determined by file extension).
        :type type: str
        :param makedir: If True, creates parent directories as needed.
        :type makedir: bool
        :param overwrite: If False and the file exists, raise FileExistsError instead of overwriting.
        :type overwrite: bool
        """
        if not path:
            if self._path:
                path = self._path
            else:
                raise ValueError("No path provided to save the dialogue and no loading path available. "
                                 "Please specify a valid file path.")

        if type == "auto":
            _, ext = os.path.splitext(path)
            ext = ext.lower()[1:]
            type = ext if ext in ["json", "txt", "csv", "tsv"] else "txt"

        if makedir and os.path.split(path)[0]:
            os.makedirs(os.path.split(path)[0], exist_ok=True)

        if not overwrite and os.path.exists(path):
            raise FileExistsError(f"File '{path}' already exists. Use 'overwrite=True' to overwrite it.")

        with open(path, "w", newline='') as writer:
            if type == "json":
                writer.write(self.json(string=True))
            elif type in ["csv", "tsv"]:
                # set delimiter based on desired type
                delimiter = {"csv": ",", "tsv": "\t"}[type]
                csv_writer = csv.writer(writer, delimiter=delimiter)
                # write the header
                csv_writer.writerow(["speaker", "text"])
                # write the turns
                for turn in self.turns:
                    csv_writer.writerow([turn.speaker, turn.text])
            else:
                writer.write(self.description())

    @staticmethod
    def from_file(path: str,
                  type: str = "auto",
                  txt_template: str = "{speaker}: {text}",
                  csv_speaker_col: Union[int, str] = "speaker",
                  csv_text_col: Union[int, str] = "text",
                  collapse_consecutive_speakers: bool = False,
                  collapse_separator: str = "\n") -> Union["Dialog", List["Dialog"]]:
        """
        Loads a dialogue from a file.

        :param path: Path to the dialogue file or directory. In case of a directory, all dialogues in the directory
                     will be loaded and returned as a list of Dialog objects.
        :type path: str
        :param type: ``"json"``, ``"txt"``, ``"csv"``, ``"tsv"``, or ``"auto"`` (determined by file extension).
        :type type: str
        :param txt_template: Template for parsing text dialogue turns (default "{speaker}: {text}").
        :type txt_template: str
        :param csv_speaker_col: Column identifier for speaker in CSV/TSV files (can be index or header name).
        :type csv_speaker_col: Union[int, str]
        :param csv_text_col: Column identifier for text in CSV/TSV files (can be index or header name).
        :type csv_text_col: Union[int, str]
        :param collapse_consecutive_speakers: If True, collapses consecutive turns by the same speaker into one
                                              turn.
        :type collapse_consecutive_speakers: bool
        :param collapse_separator: String used to join texts when collapsing consecutive turns (default: ``"\\n"``).
        :type collapse_separator: str
        :return: The loaded dialogue object.
        :rtype: Dialog
        :raises ValueError: If the file format is not recognized or if required columns are missing.
        """
        if os.path.isdir(path):
            # Let's load first all dialogues without a stored ID (all non-json files)
            filenames = sorted([filename
                                for filename in os.listdir(path)
                                if ((type == "auto" and filename.endswith((".txt", ".csv", ".tsv")))
                                    or (type != "json" and filename.endswith(type)))])
            dialogs = [Dialog.from_file(os.path.join(path, filename), type=type,
                                        txt_template=txt_template,
                                        csv_speaker_col=csv_speaker_col,
                                        csv_text_col=csv_text_col,
                                        collapse_consecutive_speakers=collapse_consecutive_speakers,
                                        collapse_separator=collapse_separator)
                       for filename in tqdm(filenames, desc="Loading dialogues from directory", leave=False)]
            # Make sure the ID is always the same, for the same file (as long as no more files are added)
            for ix, dialog in enumerate(dialogs):
                dialog.id = ix + 1
            # Adding json files too, assuming they have an id already
            dialogs.extend([Dialog.from_file(os.path.join(path, filename), type=type,
                                             txt_template=txt_template,
                                             csv_speaker_col=csv_speaker_col,
                                             csv_text_col=csv_text_col,
                                             collapse_consecutive_speakers=collapse_consecutive_speakers,
                                             collapse_separator=collapse_separator)
                            for filename in os.listdir(path)
                            if (type in ["auto", "json"]) and filename.endswith(".json")])
            return dialogs

        def _maybe_collapse(d: "Dialog"):
            if collapse_consecutive_speakers and d.turns:
                collapsed = []
                for turn in d.turns:
                    if collapsed and collapsed[-1].speaker == turn.speaker:
                        collapsed[-1].text = (collapsed[-1].text + collapse_separator + turn.text).strip()
                    else:
                        collapsed.append(turn)
                d.turns = collapsed

        type = type.lower()
        if type == "auto":
            _, ext = os.path.splitext(path)
            ext = ext.lower()[1:]
            type = ext if ext in ["json", "txt", "csv", "tsv"] else "txt"

        turns = []
        with open(path) as reader:
            if type == "json":
                dialog = Dialog.from_dict(json.load(reader))
                dialog._path = path  # Store the path for later use
                _maybe_collapse(dialog)
                return dialog
            elif type in ["csv", "tsv"]:
                is_tsv = type == "tsv"
                if isinstance(csv_speaker_col, str) and isinstance(csv_text_col, str):
                    reader = csv.DictReader(reader, delimiter='\t' if is_tsv else ',')
                    # validate headers to raise ValueError (not KeyError) on missing columns
                    if not reader.fieldnames or (
                        csv_speaker_col not in reader.fieldnames or csv_text_col not in reader.fieldnames
                    ):
                        raise ValueError(f"File '{path}': Missing required columns "
                                         f"'{csv_speaker_col}' and/or '{csv_text_col}'.")
                elif isinstance(csv_speaker_col, int) and isinstance(csv_text_col, int):
                    reader = csv.reader(reader, delimiter='\t' if is_tsv else ',')
                else:
                    raise ValueError(f"File '{path}': `csv_speaker_col` and `csv_text_col` must be either both "
                                     "strings (column names) or both integers (column indices).")

                for ix, row in enumerate(reader):
                    try:
                        speaker = row[csv_speaker_col]
                        text = row[csv_text_col]
                    except (KeyError, IndexError):
                        raise ValueError(f"File '{path}': Missing required columns at row {ix}. "
                                         f"Expected columns '{csv_speaker_col}' and '{csv_text_col}'.")
                    if speaker is None:
                        raise ValueError(f"Missing speaker in row {ix}: {row}")
                    if not text:
                        logger.warning(f"File '{path}': Empty text in row {ix}: {row}. Skipping this turn.")
                        continue
                    turns.append((speaker.strip(), text.strip()))

                dialog = Dialog(turns=[Turn(speaker=speaker, text=text) for speaker, text in turns])
                dialog._path = path
                _maybe_collapse(dialog)
                return dialog
            elif type == "txt":
                try:
                    dialog = Dialog.from_str(reader.read(), template=txt_template)
                    dialog._path = path
                    _maybe_collapse(dialog)
                    return dialog
                except ValueError as e:
                    raise ValueError(f"File '{path}': {str(e)}")
            else:
                raise ValueError(f"Unknown file type '{type}'. Supported types: 'json', 'txt', 'csv', 'tsv'.")

    @staticmethod
    def from_str(dialog_text: str,
                 template: str = "{speaker}: {text}",
                 default_speakers: List[str] = None,
                 id: Union[str, int] = None) -> "Dialog":
        """
        Creates a Dialog object from a string representation of a dialogue.

        :param dialog_text: The dialogue text, with each turn on a new line.
        :type dialog_text: str
        :param template: The template for parsing each turn. Default is "{speaker}: {text}".
        :type template: str
        :param default_speakers: Optional list of default speakers to use if no present in the text or template.
                                 The speakers will be assigned in order of appearance, in alternating turns.
                                 Default is None (speaker field will be empty in each turn).
        :type default_speakers: List[str]
        :param id: Optional ID for the dialogue. If not provided, a universal ID will be generated.
        :type id: Union[str, int]
        :return: The created Dialog object.
        :rtype: Dialog
        """
        if default_speakers is not None and not isinstance(default_speakers, list):
            raise ValueError("default_speakers must be a list of strings.")

        turns = []
        default_speaker_ix = 0
        lines = dialog_text.split("\n")
        for ix, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Use the template to extract speaker and text for each turn
            # Build a regex from the template
            regex = re.escape(template)
            regex = regex.replace(r'\ ', r'\s')
            regex = regex.replace(r'\{speaker\}', '(?P<speaker>.+?)')
            regex = regex.replace(r'\{text\}', '(?P<text>.+)')
            regex = re.sub(r'\{.+\}', '.+', regex)
            regex = regex.replace(r'\.+', '.+')
            m = re.match(regex, line)
            if m:
                try:
                    speaker = m.group('speaker').strip()
                except IndexError:
                    speaker = default_speakers[default_speaker_ix % len(default_speakers)] if default_speakers else None
                    default_speaker_ix += 1
                text = m.group('text').strip()
            else:
                raise ValueError(f"Line {ix + 1} '{line}' does not match the expected "
                                 f"format: {template}. Make sure the template "
                                 "matches the dialogue format.")

            turns.append((speaker, text))
        dialog = Dialog(turns=[Turn(speaker=speaker, text=text) for speaker, text in turns])
        if id is not None:
            dialog.id = id
        return dialog

    @staticmethod
    def from_dict(data: dict):
        """
        Creates a Dialog object from a dictionary.

        :param data: The dictionary containing dialogue data.
        :type data: dict
        :return: The created Dialog object.
        :rtype: Dialog
        """
        return Dialog.model_validate(data)

    def from_json(self, json_str: str):
        """
        Creates a Dialog object from a JSON string.

        :param json_str: The JSON string containing dialogue data.
        :type json_str: str
        :return: The created Dialog object.
        :rtype: Dialog
        """
        return Dialog.from_dict(json.loads(json_str))

    def rename_speaker(self, old_name: str,
                       new_name: str,
                       case_sensitive: bool = False,
                       in_events: bool = True) -> "Dialog":
        """
        Renames all occurrences of a speaker in the dialogue's turns (and optionally events).

        :param old_name: The current speaker name to replace.
        :type old_name: str
        :param new_name: The new speaker name.
        :type new_name: str
        :param case_sensitive: Whether to match speaker names case-sensitively (default: False).
        :type case_sensitive: bool
        :param in_events: Whether to also rename in events' agent fields (default: True).
        :type in_events: bool
        :return: Self (the same Dialog instance) after in-place modification.
        :rtype: Dialog
        """
        def match(name):
            if case_sensitive:
                return name == old_name
            else:
                return name.lower() == old_name.lower() if name is not None else False

        # Rename in turns
        for turn in self.turns:
            if turn.speaker is not None and match(turn.speaker):
                turn.speaker = new_name

        # Rename in events (if present and requested)
        if in_events and self.events:
            for event in self.events:
                if hasattr(event, 'agent') and event.agent is not None and match(event.agent):
                    event.agent = new_name

        return self

    def get_speakers(self, keep_case: bool = True) -> List[str]:
        """
        Returns a list of unique speaker names in the dialogue.

        :param keep_case: Whether to keep the original case of speaker names or convert them to lowercase
                          (default: True).
        :type keep_case: bool
        :return: A list of unique speaker names.
        :rtype: List[str]
        """
        if keep_case:
            return list(set(turn.speaker for turn in self.turns if turn.speaker))
        else:
            return list(set(turn.speaker.lower() for turn in self.turns if turn.speaker))

    def filter(self, speaker: str) -> "Dialog":
        """
        Filters the dialogue turns by speaker.

        :param speaker: The speaker name to filter by (case-insensitive).
        :type speaker: str
        :return: A new Dialog containing only that speaker's turns; returns None if speaker not found.
        :rtype: Optional[Dialog]
        """
        if speaker.lower() not in self.get_speakers(keep_case=False):
            logger.error(f"The provided speaker '{speaker}' does not exist in the dialogue. "
                         f"Valid speakers are: {self.get_speakers()}")

        filtered_dialog = self.clone()
        filtered_dialog.turns = [turn for turn in self.turns if turn.speaker.lower() == speaker.lower()]
        if filtered_dialog.events:
            filtered_dialog.events = [event for event in self.events if event.agent.lower() == speaker.lower()]
        return filtered_dialog

    __str__ = description


class Context(BaseAttributeModel):
    """
    Dialogue-shared context class.

    :param location: Physical or virtual location where the dialogue occurs.
    :type location: Optional[str]
    :param datetime: Timestamp or temporal setting relevant to the dialogue.
    :type datetime: Optional[str]
    :param environment: Physical environment description, environmental conditions, or contextual atmosphere.
    :type environment: Optional[str]
    :param objects: Relevant objects (single value or list of values).
    :type objects: Optional[Union[str, List[str]]]
    :param participants_shared_knowledge: Information all participants are assumed to know.
    :type participants_shared_knowledge: Optional[str]
    :param circumstances: Situational circumstances impacting the dialogue.
    :type circumstances: Optional[Union[str, List[str]]]
    :param goals: Stated or implicit goals of the participants.
    :type goals: Optional[Union[str, List[str]]]
    :param constraints: Limitations or constraints affecting actions or dialogue.
    :type constraints: Optional[Union[str, List[str]]]
    :param topics: Main topics or themes (single or list).
    :type topics: Optional[Union[str, List[str]]]
    :param style_guidelines: Stylistic or formatting guidelines to follow.
    :type style_guidelines: Optional[Union[str, List[str]]]
    :param notes: Additional free-form contextual notes.
    :type notes: Optional[str]
    """

    # Time / place
    location: Optional[str] = Field(default=None, description="Physical or virtual location where the dialogue occurs.")
    datetime: Optional[str] = Field(default=None, description="Timestamp or temporal setting relevant to the dialogue.")
    # Environment
    environment: Optional[str] = Field(
        default=None,
        description="Physical environment description, environmental conditions, or contextual atmosphere."
    )
    # Objects
    objects: Optional[Union[str, List[str]]] = Field(default=None, description="Relevant objects (single or list).")
    # Participants shared knowledge
    participants_shared_knowledge: Optional[str] = Field(
        default=None,
        description="Information all participants are assumed to know."
    )
    # Intent / constraints
    circumstances: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="Situational circumstances impacting the dialogue."
    )
    goals: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="Stated or implicit goals of the participants."
    )
    constraints: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="Limitations or constraints affecting actions or dialogue."
    )
    # Topics
    topics: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="Main topics or themes (single or list)."
    )
    # Style and Extensions
    style_guidelines: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="Stylistic or formatting guidelines to follow."
    )
    notes: Optional[str] = Field(default=None, description="Additional free-form contextual notes.")


def _print_dialog(dialog: Union[Dialog, dict],
                  scenario: bool = False,
                  orchestration: bool = False,
                  think: bool = False,
                  all: bool = False):
    """
    Pretty-prints a dialogue to the console, with optional scenario and orchestration details.

    :param dialog: The dialogue to print.
    :type dialog: Union[Dialog, dict]
    :param scenario: If True, prints scenario information.
    :type scenario: bool
    :param orchestration: If True, prints also orchestration events.
    :type orchestration: bool
    :param think: If True, prints "thinking" events.
    :type think: bool
    :param all: If True, prints all types of events.
    :type all: bool
    """
    if type(dialog) is dict:
        dialog = Dialog.model_validate(dialog)

    def _get_turn_from_event(e: Event) -> Turn:
        if e.action == "utter":
            speaker, text = e.agent, e.content
        elif e.action == "pick_suggestion":
            speaker, text = e.agent, f"[pick_suggestion] {e.content}"
        elif e.action == "think":
            speaker, text = e.agent, f"(thinking) {e.content}"
        elif e.action == "tool" and e.actionLabel != "call":
            speaker, text = f"{e.action}-{e.actionLabel}", e.content
        else:
            speaker, text = f"{e.action}-{e.actionLabel}" if e.actionLabel else e.action, f"({e.agent}) {e.content}"

        return Turn(speaker=speaker, text=remove_newlines(str(text)))

    speaker_tag_colors = ["red", "blue", "yellow", "cyan", "green", "magenta", "purple"]
    speaker_utt_colors = ["grey"]  # ["grey", "white"]  white is not seen in light mode...
    # speaker_utt_colors = ["black", "grey"]

    if dialog.id:
        cprint(dialog.id, tag="dialog_id", tag_color="purple", color="magenta", format="bold")
    if dialog.complete:
        cprint(dialog.complete, tag="complete", tag_color="purple", color="magenta", format="bold")
    if dialog.model:
        cprint(dialog.model, tag="model", tag_color="purple", color="magenta", format="bold")
    if dialog.seed:
        cprint(dialog.seed, tag="seed", tag_color="purple", color="magenta", format="bold")
    if scenario and dialog.scenario:
        cprint("", tag="scenario", tag_color="purple", color="magenta", format="bold")
        if type(dialog.scenario) is str:
            cprint(dialog.scenario, color="magenta")
        else:
            cprint(json.dumps(dialog.scenario, indent=2), color="magenta")

    cprint("--- Dialogue Begins ---", color="magenta", format="bold")
    speakers = sorted(list(set(turn.speaker for turn in dialog.turns)))

    if all or orchestration or think:
        dialog = dialog.model_copy()
        events = dialog.events or []

        if all:
            filtered_events = events
        else:
            filtered_events = []
            for e in events:
                act = (e.action or "").lower()
                if act in "utter" or (orchestration and act.startswith("instruct")) or (think and act == "think"):
                    filtered_events.append(e)

        dialog.turns = [_get_turn_from_event(e) for e in filtered_events]

    for ix, turn in enumerate(dialog.turns):
        speaker = turn.speaker

        if speaker not in speakers:
            tag_color = "yellow"
            color = "purple"
        else:
            tag_color = speaker_tag_colors[speakers.index(speaker) % len(speaker_tag_colors)]
            if turn.text.startswith("(thinking) "):
                color = "purple"
            else:
                color = speaker_utt_colors[speakers.index(speaker) % len(speaker_utt_colors)]

        cprint(remove_newlines(turn.text),
               tag=speaker,
               tag_color=tag_color,
               color=color)
    cprint("--- Dialogue Ends ---", color="magenta", format="bold")


class Instruction(BaseModel):
    """
    Represents an instruction to an agent, optionally with associated events.

    :param text: The instruction text.
    :type text: str
    :param events: Associated event(s), either a single Event or a list of Events.
    :type events: Optional[Union[Event, List[Event]]]
    """
    text: str = None
    events: Optional[Union[Event, List[Event]]] = None  # extra events

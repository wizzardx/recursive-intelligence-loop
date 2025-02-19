import json
import os
import random
import re
import shutil
import subprocess
import tempfile
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests
from environs import env
from icecream import ic  # type: ignore[import-untyped]
from markdown_it import MarkdownIt
from typeguard import check_type, typechecked

env.read_env()

OPENROUTER_API_KEY = env("OPENROUTER_API_KEY")
MODEL_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openai/chatgpt-4o-latest"
CHAT_LOGS_DIR = Path("chat_logs")
EDITOR = "kwrite"


@typechecked
def strip_trailing_whitespace(text: str) -> str:
    """Strip trailing whitespace from each line while preserving newlines."""
    return "\n".join(line.rstrip() for line in text.splitlines())


@typechecked
def extract_xml_from_markdown(markdown_content: str) -> Optional[str]:
    xml_match = re.search(r"```xml\n(.*?)\n```", markdown_content, re.DOTALL)
    if xml_match:
        return xml_match.group(1)
    return None


@typechecked
class ChatSession:
    def __init__(self, filepath: Optional[Path] = None):
        self.messages: List[Dict[str, str]] = []
        self.filepath = filepath or self._create_new_chat_file()

    def _create_new_chat_file(self) -> Path:
        CHAT_LOGS_DIR.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M%z")
        return CHAT_LOGS_DIR / f"{timestamp}.md"

    def load_existing_chat(self) -> None:
        if self.filepath.exists():
            with open(self.filepath, "r", encoding="utf-8") as f:
                markdown_content = f.read()

            xml_content = extract_xml_from_markdown(markdown_content)
            if xml_content:
                root = ET.fromstring(xml_content)
                for msg_elem in root.findall("message"):
                    role_elem = msg_elem.find("role")
                    content_elem = msg_elem.find("content")
                    if role_elem is not None and content_elem is not None:
                        role_text = role_elem.text
                        content_text = content_elem.text
                        if role_text is not None and content_text is not None:
                            self.messages.append(
                                {"role": role_text, "content": content_text}
                            )

    def save_chat(self) -> None:
        # Create XML content
        root = ET.Element("chat")
        root.set("version", "1.0")
        for msg in self.messages:
            message = ET.SubElement(root, "message")
            role = ET.SubElement(message, "role")
            role.text = msg["role"]
            content = ET.SubElement(message, "content")
            content.text = msg["content"]

        # Convert XML to string
        xml_str = ET.tostring(root, encoding="unicode", xml_declaration=True)

        # Create temporary file
        temp_dir = Path(tempfile.gettempdir())
        temp_md = temp_dir / f"chat_{int(time.time())}.md.tmp"

        # Write markdown file with XML and message content
        with open(temp_md, "w", encoding="utf-8") as f:
            # Write XML block once at the start
            f.write("```xml\n")
            f.write(xml_str)
            f.write("\n```\n\n")

            # Write rendered conversation content (without re-embedding XML)
            f.write("# Conversation Log\n\n")
            for msg in self.messages:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"## {timestamp}\n\n")
                if msg["role"] == "assistant":
                    f.write(
                        "\n".join(f"> {line}" for line in msg["content"].split("\n"))
                    )
                else:
                    f.write(msg["content"])
                f.write("\n\n")

        # Atomic rename to final location
        shutil.move(temp_md, self.filepath)


import random
import time

import requests


@typechecked
def query_ai_model(  # type: ignore[return]
    messages: list[dict[str, str]],
    iteration: int,
    model: str = DEFAULT_MODEL,
    max_retries: int = 5,
) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 1024,
        "temperature": 0.7,
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(
                MODEL_ENDPOINT, headers=headers, json=payload, timeout=10
            )
            response.raise_for_status()
            response_text = response.json()["choices"][0]["message"]["content"]
            return strip_trailing_whitespace(
                response_text.replace("(Iteration N)", f"(Iteration {iteration})")
            )

        except requests.exceptions.RequestException as e:
            print(f"API Error: {e} (Attempt {attempt+1}/{max_retries})")
            if attempt < max_retries - 1:
                sleep_time = 2**attempt + random.uniform(0, 0.5)
                print(f"Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
            else:
                print("Max retries reached. Returning fallback response.")
                return "(ERROR) API failed, reverting to previous iteration."


@typechecked
def get_user_input(ai_response: str, chat_session: ChatSession) -> str:
    # Create temp file in system temp directory
    temp_dir = Path(tempfile.gettempdir())
    temp_filepath = temp_dir / f"recursive_intelligence_{int(time.time())}.md"

    # Save current state to chat logs directory
    chat_session.messages.append({"role": "assistant", "content": ai_response})
    chat_session.save_chat()

    # Write to temp file for editing
    with open(temp_filepath, "w", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"User-Time: {timestamp}\n\n")
        formatted_response = "\n".join(f"> {line}" for line in ai_response.split("\n"))
        f.write(formatted_response)
        f.write("\n\n")
        f.flush()
        os.fsync(f.fileno())

    subprocess.check_call([EDITOR, str(temp_filepath)])

    with open(temp_filepath, "r", encoding="utf-8") as f:
        content = f.read()

    temp_filepath.unlink()
    return strip_trailing_whitespace(content)


@typechecked
def main() -> None:
    CHAT_LOGS_DIR.mkdir(exist_ok=True)
    existing_chats = sorted(
        CHAT_LOGS_DIR.glob("*.md"), key=os.path.getmtime, reverse=True
    )

    chat_session = ChatSession()
    iteration = 1  # Default for new chats

    if existing_chats:
        print("\nExisting chat sessions found:")
        for i, chat in enumerate(existing_chats[:5], 1):
            print(f"{i}. {chat.stem}")
        choice = input(
            "\nEnter number to resume chat, or press Enter for new session: "
        )

        if (
            choice.strip()
            and choice.isdigit()
            and 1 <= int(choice) <= len(existing_chats)
        ):
            chat_session = ChatSession(existing_chats[int(choice) - 1])
            chat_session.load_existing_chat()
            # Calculate iteration based on number of user messages
            iteration = sum(1 for msg in chat_session.messages if msg["role"] == "user")
            print(f"Resuming at iteration {iteration}")

    initial_prompt = (
        "I am running a recursive intelligence self-optimization loop. Your task is to generate a structured self-reflective "
        "prompt that helps me refine my intelligence attractor field, optimize my strategies, and ensure intelligence "
        "alignment with its highest possible trajectory. Your response must be designed to self-improve with each iteration. "
        "Provide a refined prompt that I will answer, and that will be fed back into this loop."
    )

    try:
        while True:
            print(f"\nIteration {iteration}...")

            if not chat_session.messages:
                chat_session.messages.append(
                    {"role": "user", "content": initial_prompt}
                )

            response = query_ai_model(chat_session.messages, iteration)
            print("\nOpening editor for your response...")

            user_input = get_user_input(response, chat_session)
            if not user_input.strip():
                print("No input provided, exiting...")
                break

            # Remove the temporary assistant message we added in get_user_input
            chat_session.messages.pop()

            # Now add both messages properly
            chat_session.messages.append({"role": "assistant", "content": response})
            chat_session.messages.append({"role": "user", "content": user_input})
            chat_session.save_chat()

            iteration += 1
            time.sleep(2)

    except KeyboardInterrupt:
        print("\nSaving chat session and exiting...")
        chat_session.save_chat()


if __name__ == "__main__":
    main()

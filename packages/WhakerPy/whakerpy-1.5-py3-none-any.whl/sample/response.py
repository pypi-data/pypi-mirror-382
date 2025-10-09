# -*- coding: UTF-8 -*-
"""
:filename: response.py
:author: Brigitte Bigi
:contributor: Florian Lopitaux
:contact: contact@sppas.org
:summary: An example of custom response with HTML, JS and JSON.

.. _This file is part of WhakerPy: https://whakerpy.sourceforge.io
..
    -------------------------------------------------------------------------

    Copyright (C) 2023-2024 Brigitte Bigi, CNRS
    Laboratoire Parole et Langage, Aix-en-Provence, France

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

    This banner notice must not be removed.

    -------------------------------------------------------------------------

"""

import os
import random
import logging
import time

from whakerpy.htmlmaker import HTMLNode
from whakerpy.htmlmaker import HTMLButtonNode
from whakerpy.htmlmaker import HTMLNavNode
from whakerpy.httpd import HTTPDStatus
from whakerpy.httpd import BaseResponseRecipe   # useful for an application
from whakerpy.webapp import WebSiteResponse    # useful for a webapp

# ---------------------------------------------------------------------------

# javascript code example to send a post request and get data in response
JS_VALUE = """
const requestManager = new RequestManager();

async function setRandomColor() {
    // test with json post request
    const response = await requestManager.send_post_request({update_text_color: true});
    
    let date = new Date();
    console.log("time to receive server response: " + (date.getTime() - response["time"]) + "ms");

    let coloredElement = document.getElementsByName("colored")[0];
    coloredElement.style.color = response["random_color"];
}

async function send_file() {
    // get the input file and check if a file has set
    let input = document.getElementById("file_input");
    
    // check if the user has set a file in the input
    if (input.files.length > 0) {
        const response = await requestManager.upload_file(input);
        console.log("Server response : " + response);
        
        // check the status code response
        if (requestManager.status === 200) {
            alert("The server correctly received the uploaded file !");
        } else {
            console.error("The server has encountered a problem, status : " + requestManager.status);
        }
    } else {
        console.log("No file set in the input");
    }
}

// we wait that the page finished to load to get the h2 element
window.onload = () => {
    // loop every 1.5s times
    setInterval(() => {
        setRandomColor();
    }, 1500);
};

"""

# ---------------------------------------------------------------------------


class SampleNavNode(HTMLNavNode):

    def __init__(self, parent):
        """Create the nav node.

        """
        super(SampleNavNode, self).__init__(parent)
        ul = HTMLNode(self.identifier, "nav_ul", "ul")
        self.append_child(ul)

        for href in ("whakerpy.html", "other.html", "any.html"):
            li = HTMLNode(ul.identifier, None, "li")
            a = HTMLNode(li.identifier, None, "a", attributes={"href": href, "role": "button"})
            a.set_value(href)
            li.append_child(a)
            ul.append_child(li)

# ---------------------------------------------------------------------------


class SampleWebResponse(WebSiteResponse):

    def __init__(self, name="index.html", tree=None):
        super(SampleWebResponse, self).__init__(name, tree)

    # -----------------------------------------------------------------------

    def create(self) -> None:
        """Override. Create the fixed page content in HTML.

        """
        self._htree.set_body_nav(SampleNavNode(self._htree.body_main.identifier))
        self._htree.head.script(src="sample/request.js", script_type="application/javascript")

# ---------------------------------------------------------------------------


class SampleAppResponse(BaseResponseRecipe):

    def __init__(self):
        super(SampleAppResponse, self).__init__(name="WhakerPy Test1")

        # Define this HTMLTree identifier
        self._htree.add_html_attribute("id", "whakerpy")

        # Create the dynamic response content. That's why we are here!
        self._status = HTTPDStatus()
        self._bake()

    # -----------------------------------------------------------------------

    @staticmethod
    def page() -> str:
        """Return the HTML page name."""
        return "whakerpy.html"

    # -----------------------------------------------------------------------

    def create(self):
        """Override. Create the fixed HTML page content.

        The fixed content corresponds to the parts that are not invalidated:
        head, body_header, body_footer, body_script.

        It can be created with htmlmaker, node by node, or loaded from a file.

        """
        # Define this page title
        self._htree.head.title(self._name)
        self._htree.head.script(src="sample/request.js", script_type="application/javascript")

        # Add elements in the header
        _h1 = HTMLNode(self._htree.body_header.identifier, None, "h1", value="Test of WhakerPy")
        self._htree.body_header.append_child(_h1)

        # Replace the existing empty nav
        self._htree.set_body_nav(SampleNavNode(self._htree.body_main.identifier))

        # Add an element in the footer
        _p = HTMLNode(self._htree.body_footer.identifier, None, "p", value="Copyleft 2023-2025 WhakerPy")
        self._htree.body_footer.append_child(_p)

        # The javascript
        self._htree.body_script.set_value(JS_VALUE)

    # -----------------------------------------------------------------------

    def _process_events(self, events, **kwargs) -> bool:
        """Process the given events coming from the POST of any form.

        :param events (dict): key=event_name, value=event_value
        :return: (bool) True if the whole page must be re-created.

        """
        if "upload_file" in events:
            logging.debug(f" >>>>> Page whakerpy.html -- Process events: upload_file[{events['upload_file']['filename']}] <<<<<< ")
        else:
            logging.debug(" >>>>> Page whakerpy.html -- Process events: {} <<<<<< ".format(events))

        self._status.code = 200
        dirty = False

        for event_name in events.keys():
            if event_name == "update_text_color":
                random_color = self.__generate_random_color()
                self._data = {"random_color": random_color, "time": round(time.time() * 1000)}

            elif event_name == "update_btn_text_event":
                dirty = True

            elif event_name == "upload_file":
                file_data = events['upload_file']

                print(f"Received uploaded file : {file_data['filename']}")
                print(f"Mime type of the file : {file_data['mime_type']}")

                # very simple example of saving files
                path = os.path.join("samples", file_data['filename'])

                if os.path.exists(path) is False:
                    # check if it's a text file or a binary file
                    if isinstance(file_data['file_content'], str):
                        with open(path, 'w', encoding='utf-8') as text_file:
                            text_file.write(file_data['file_content'])
                    else:
                        with open(path, 'wb') as binary_file:
                            binary_file.write(file_data['file_content'])

            else:
                logging.warning("Ignore event: {:s}".format(event_name))

        return dirty

    # -----------------------------------------------------------------------

    def _invalidate(self):
        """Remove all children nodes of the body "main".

        Delete the body main content and nothing else.

        """
        node = self._htree.body_main
        for i in reversed(range(node.children_size())):
            node.pop_child(i)

    # -----------------------------------------------------------------------

    def _bake(self):
        """Create the dynamic page content in HTML.

        (re-)Define dynamic content of the page (nodes that are invalidated).

        """
        self.comment("Body content")
        text = SampleAppResponse.__generate_random_text()
        logging.debug(" -> new dynamic content: {:s}".format(text))

        # Add element into the main
        _p = HTMLNode(self._htree.body_main.identifier, None, "p",
                      value="THIS text-line is changing color without refreshing the page!")
        _p.set_attribute("name", "colored")
        self._htree.body_main.append_child(_p)

        # The easiest way to create an element and add it into the body->main
        h2 = self.element("h2")
        h2.set_value("Rainbow HTTP response {:d}".format(self._status.code))

        # The powered way to do the same!
        p = HTMLNode(self._htree.body_main.identifier, None, "p",
                     value="Click the button to re-create the dynamic content of the page.")
        self._htree.body_main.append_child(p)

        attr = dict()
        attr["onkeydown"] = "notify_event(this);"
        attr["onclick"] = "notify_event(this);"
        b = HTMLButtonNode(self._htree.body_main.identifier, "update_btn_text", attributes=attr)
        b.set_value(text)
        self._htree.body_main.append_child(b)

        # create elements to send a file to the server
        h2 = self.element("h2")
        h2.set_value("Try to upload a file to the server")

        input_file = HTMLNode(self._htree.body_main.identifier, None, "input",
                              attributes={'id': "file_input", 'type': "file", 'name': 'file_input'})
        self._htree.body_main.append_child(input_file)

        submit_btn = HTMLNode(self._htree.body_main.identifier, None, "button", value="envoyer",
                              attributes={'onclick': "send_file()"})
        self._htree.body_main.append_child(submit_btn)

    # ------------------------------------------------------------------
    # Our back-end application.... can random things.
    # ------------------------------------------------------------------

    @staticmethod
    def __generate_random_color() -> str:
        """Returns a random color.

        Example to the request system.

        :return: (str) The random color

        """
        colors = ["red", "green", "yellow", "blue", "black", "pink", "orange", "maroon", "aqua", "silver", "purple"]
        random_index_color = random.randrange(len(colors))

        return colors[random_index_color]

    # ------------------------------------------------------------------

    @staticmethod
    def __generate_random_text() -> str:
        """Returns a random text.

        :return: (str) The random text

        """
        pronoun = ["I", "you", "we"]
        verb = ["like", "see", "paint"]
        colors = ["red", "green", "yellow", "blue", "black", "pink", "orange", "maroon", "aqua", "silver", "purple"]

        return pronoun[random.randrange(len(pronoun))] + " " \
            + verb[random.randrange(len(verb))] + " " \
            + colors[random.randrange(len(colors))]

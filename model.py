# model.py

voskModels = {
    "English": {
        "small": {
            "name": "vosk-model-small-en-us-0.15",
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
        },
        "large": {
            "name": "vosk-model-en-us-0.22",
            "url": "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip"
        }
    },
    "Spanish": {
        "small": {
            "name": "vosk-model-small-es-0.42",
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip"
        },
        "large": {
            "name": "vosk-model-es-0.42",
            "url": "https://alphacephei.com/vosk/models/vosk-model-es-0.42.zip"
        }
    },
    "French": {
        "small": {
            "name": "vosk-model-small-fr-0.22",
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip"
        },
        "large": {
            "name": "vosk-model-fr-0.22",
            "url": "https://alphacephei.com/vosk/models/vosk-model-fr-0.22.zip"
        }
    },
    "German": {
        "small": {
            "name": "vosk-model-small-de-0.15",
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-de-0.15.zip"
        },
        "large": {
            "name": "vosk-model-de-0.21",
            "url": "https://alphacephei.com/vosk/models/vosk-model-de-0.21.zip"
        }
    },
    "Indian English": {
        "small": {
            "name": "vosk-model-small-en-in-0.4",
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-en-in-0.4.zip"
        },
        "large": {
            "name": "vosk-model-en-in-0.5",
            "url": "https://alphacephei.com/vosk/models/vosk-model-en-in-0.5.zip"
        }
    },
    "Chinese": {
        "small": {
            "name": "vosk-model-small-cn-0.22",
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip"
        },
        "large": {
            "name": "vosk-model-cn-0.22",
            "url": "https://alphacephei.com/vosk/models/vosk-model-cn-0.22.zip"
        }
    },
    "Russian": {
        "small": {
            "name": "vosk-model-small-ru-0.22",
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip"
        },
        "large": {
            "name": "vosk-model-ru-0.42",
            "url": "https://alphacephei.com/vosk/models/vosk-model-ru-0.42.zip"
        }
    },
    "Portuguese": {
        "small": {
            "name": "vosk-model-small-pt-0.3",
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip"
        },
        "large": {
            "name": "vosk-model-pt-fb-v0.1.1-20220516_2113",
            "url": "https://alphacephei.com/vosk/models/vosk-model-pt-fb-v0.1.1-20220516_2113.zip"
        }
    },
    "Japanese": {
        "small": {
            "name": "vosk-model-small-ja-0.22",
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-ja-0.22.zip"
        },
        "large": {
            "name": "vosk-model-ja-0.22",
            "url": "https://alphacephei.com/vosk/models/vosk-model-ja-0.22.zip"
        }
    },
    "Italian": {
        "small": {
            "name": "vosk-model-small-it-0.22",
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-it-0.22.zip"
        },
        "large": {
            "name": "vosk-model-it-0.22",
            "url": "https://alphacephei.com/vosk/models/vosk-model-it-0.22.zip"
        }
    },
    "Dutch": {
        "small": {
            "name": "vosk-model-small-nl-0.22",
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-nl-0.22.zip"
        },
        "large": {
            "name": "vosk-model-nl-spraakherkenning-0.6",
            "url": "https://alphacephei.com/vosk/models/vosk-model-nl-spraakherkenning-0.6.zip"
        }
    },
    "Greek": {
        "small": {
            "name": "vosk-model-small-el-0.7",
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-el-0.7.zip"
        },
        "large": {
            "name": "vosk-model-el-gr-0.7",
            "url": "https://alphacephei.com/vosk/models/vosk-model-el-gr-0.7.zip"
        }
    },
    "Arabic": {
        "small": {
            "name": "vosk-model-small-ar-0.22",
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-ar-0.22.zip"
        },
        "large": {
            "name": "vosk-model-ar-0.22-linto-1.1.0",
            "url": "https://alphacephei.com/vosk/models/vosk-model-ar-0.22-linto-1.1.0.zip"
        }
    },
    "Vietnamese": {
        "small": {
            "name": "vosk-model-small-vn-0.4",
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-vn-0.4.zip"
        },
        "large": {
            "name": "vosk-model-vn-0.4",
            "url": "https://alphacephei.com/vosk/models/vosk-model-vn-0.4.zip"
        }
    },
    "Korean": {
        "small": {
            "name": "vosk-model-small-ko-0.22",
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-ko-0.22.zip"
        },
        "large": {
            "name": "vosk-model-ko-0.22",
            "url": "https://alphacephei.com/vosk/models/vosk-model-ko-0.22.zip"
        }
    },
    "Hindi": {
        "small": {
            "name": "vosk-model-small-hi-0.22",
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip"
        },
        "large": {
            "name": "vosk-model-hi-0.22",
            "url": "https://alphacephei.com/vosk/models/vosk-model-hi-0.22.zip"
        }
    },
    "Farsi": {
        "small": {
            "name": "vosk-model-small-fa-0.42",
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-fa-0.42.zip"
        },
        "large": {
            "name": "vosk-model-fa-0.42",
            "url": "https://alphacephei.com/vosk/models/vosk-model-fa-0.42.zip"
        }
    },
    "Filipino": {
        "small": {
            "name": "vosk-model-small-tl-0.6",
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-tl-0.6.zip"
        },
        "large": {
            "name": "vosk-model-tl-ph-generic-0.6",
            "url": "https://alphacephei.com/vosk/models/vosk-model-tl-ph-generic-0.6.zip"
        }
    },
    "Czech": {
        "small": {
            "name": "vosk-model-small-cs-0.4",
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-cs-0.4.zip"
        },
        "large": {
            "name": "vosk-model-cs-0.4",
            "url": "https://alphacephei.com/vosk/models/vosk-model-cs-0.4.zip"
        }
    },
    "Polish": {
        "small": {
            "name": "vosk-model-small-pl-0.22",
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-pl-0.22.zip"
        },
        "large": {
            "name": "vosk-model-pl-0.22",
            "url": "https://alphacephei.com/vosk/models/vosk-model-pl-0.22.zip"
        }
    },
    "Swedish": {
        "small": {
            "name": "vosk-model-small-sv-0.15",
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-sv-0.15.zip"
        },
        "large": {
            "name": "vosk-model-sv-0.15",
            "url": "https://alphacephei.com/vosk/models/vosk-model-sv-0.15.zip"
        }
    },
    "Esperanto": {
        "small": {
            "name": "vosk-model-small-eo-0.42",
            "url": "https://alphacephei.com/vosk/models/vosk-model-small-eo-0.42.zip"
        },
        "large": {
            "name": "vosk-model-eo-0.42",
            "url": "https://alphacephei.com/vosk/models/vosk-model-eo-0.42.zip"
        }
    },
    "Breton": {
        "small": {
            "name": "vosk-model-br-0.8",
            "url": "https://alphacephei.com/vosk/models/vosk-model-br-0.8.zip"
        },
        "large": {
            "name": "vosk-model-br-0.8",
            "url": "https://alphacephei.com/vosk/models/vosk-model-br-0.8.zip"
        }
    },
}

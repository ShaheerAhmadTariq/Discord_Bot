#!/bin/bash
python download_model.py PygmalionAI/pygmalion-2-13b --output models
python server.py --api --chat --model PygmalionAI_pygmalion-2-13b --model-dir models


#!/bin/bash
python download_model.py PygmalionAI/pygmalion-6b --output models
python server.py --api --chat --model PygmalionAI_pygmalion-6b --model-dir models


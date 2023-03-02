"""
Demonstration of the VidoeEditor library.
Check the README.md for complete documentation.
"""
import os
from video_editor import Analyzer,Mutator,Regulator

cwd = os.path.abspath(os.path.dirname(__file__))
fileToProcess = os.path.join(cwd, 'video/李SY自己产品.mp4')

#TODO: process all videos under same folder
analyzer = Analyzer(fileToProcess)
analyzer.trackEye()


mutator = Mutator()
regulator = Regulator()
regulator.review(analyzer, mutator)









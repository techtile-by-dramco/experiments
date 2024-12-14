# ffmpeg -framerate 4 -pattern_type glob -i '*.png' -c:v libx264 -pix_fmt yuv420p intermediate.mp4

ffmpeg -framerate 5 -pattern_type glob -i '*.png' -vf "scale=1920:1080,format=yuv420p,minterpolate=fps=20:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1" -c:v libx264 -crf 18 -preset slow output.mp4

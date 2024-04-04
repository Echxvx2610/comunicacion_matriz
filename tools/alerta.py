from plyer import notification  # pip install plyer ( utiliza la librería de notificación de plyer )
import winsound                 # para reproducir un archivo de audio

def mostrar_notificacion_con_sonido(title, message, sound_file):
    # Mostrar la notificación
    notification.notify(
        title=title,
        message=message,
        app_name='MFG.py',
        app_icon= r'C:\Users\CECHEVARRIAMENDOZA\OneDrive - Brunswick Corporation\Documents\Proyectos_Python\PysimpleGUI\Proyectos\analisis_matriz\img\excel.ico',  # Opcional
        timeout=2 # Opcional: tiempo en segundos antes de que la notificación se cierre automáticamente
    )
    # Reproducir el sonido
    winsound.PlaySound(sound_file, winsound.SND_FILENAME)
    # winsound.PlaySound(sound_file, winsound.SND_LOOP)
    
# Llamar a la función para mostrar la notificación con sonido
# mostrar_notificacion_con_sonido(
#     title='Analisis de la Matriz MFG',
#     message='El archivo csv ha sido modificado recientemente!',
#     sound_file=r'C:\Users\CECHEVARRIAMENDOZA\OneDrive - Brunswick Corporation\Documents\Proyectos_Python\PysimpleGUI\Proyectos\analisis_matriz\sound\cat-meow-85175.wav'
# )

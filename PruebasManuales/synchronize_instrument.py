from PySide6.QtCore import QThread, Signal

class SynchronizationWorker(QThread):
    """Executes deterministic instrument synchronization in a background thread.
    
    Attributes:
        osc: The oscilloscope hardware interface object.
    """
    sync_completed = Signal()
    sync_failed = Signal(str)

    def __init__(self, osc):
        """Initializes the SynchronizationWorker.

        Args:
            osc: The oscilloscope control instance containing the DSO resource.
        """
        super().__init__()
        self.osc = osc

    def run(self):
        """Runs the blocking SCPI reset and operation complete query."""
        try:
            # Envía el comando *RST internamente
            self.osc.default_settings()
            
            # Bloquea exclusivamente este hilo secundario hasta que el hardware finalice
            response = self.osc.dso.query("*OPC?")
            
            if response.strip() == "1":
                self.sync_completed.emit()
            else:
                self.sync_failed.emit("Invalid *OPC? response.")
        except Exception as e:
            self.sync_failed.emit(f"VISA I/O Error: {str(e)}")


# --- Lógica dentro del Controller principal ---

    def synchronize_instrument(self):
        """Initiates the deterministic synchronization of the instrument."""
        if not self.osc.dso:
            return

        # Previene la recolección de basura asignando el worker a un atributo de instancia
        self._sync_worker = SynchronizationWorker(self.osc)
        
        # Conexión de señales a los slots del Controller
        self._sync_worker.sync_completed.connect(self._continue_synchronization)
        self._sync_worker.sync_failed.connect(self._handle_sync_error)
        
        # Inicia la ejecución del método run()
        self._sync_worker.start()

    def _handle_sync_error(self, error_message: str):
        """Handles hardware synchronization errors.

        Args:
            error_message: The error description from the worker thread.
        """
        # Lógica para mostrar alerta en la View o loguear el error
        pass
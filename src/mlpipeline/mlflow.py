"""
Mlflow module providing MlFlow plug to log experiments.
Experiments made on parameters, metrics, artifacts and tags.
"""
import mlflow
import mlflow.sklearn
from tempfile import NamedTemporaryFile
import os
import matplotlib.pyplot as plt

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-

class MlFlow:

    exp_folder = 'NLP'

    def __init__(self, experiment_name=None, tracking_uri=None):
        self.experiment_name = experiment_name
        self.tracking_uri = tracking_uri

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-

# Getters and Setters

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-


    @property
    def experiment_name(self):
        return self._experiment_name

    @experiment_name.setter
    def experiment_name(self, exp_name):
        """The name of the experiment the results will be saved in for the MLFlow UI"""
        if not isinstance(exp_name, str):
            raise TypeError("Input needs to be a String")
        self._experiment_name = exp_name

    @property
    def tracking_uri(self):
        return self._tracking_uri

    @tracking_uri.setter
    def tracking_uri(self, path):
        """
        Returns the abs path to mlruns folder
        using the correct forward-slash or backward-slash.
        """

        if not isinstance(path, str):
            raise TypeError("Input needs to be a String")

        mlflow_uri_path = path.split("nlp-web-scrapping")[0]

        separator = "\\"
        if "/" in mlflow_uri_path:
            separator = '/'

        # The uri needs to end with the mlruns folder
        mlflow_uri_path = mlflow_uri_path + "nlp-web-scrapping" + separator + "mlruns"

        # To set, uri needs "file:///" at the start
        uri = "file:/" + str(mlflow_uri_path)

        self._tracking_uri = uri


#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-

# Functions

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-

    def set_experiment_id(self, name):
        """
        Get experiment_id using self.exp_folder
        """

        if name is None:
            experiment_id = None

        else:
            # Get experiment_id from already created experiment name -> 'NLP'
            try:
                exp_id = mlflow.get_experiment_by_name(name).experiment_id
                # Inputs:
                    # name = the experiment's name
                # Returns: Experiment object
                    # .experiment_id = Integer - value wanted from object

            # Create new experiment and get experiment_id
            except AttributeError:  # Error: if experiment doesn't exist ...
                exp_id = mlflow.create_experiment(name)

                # Inputs:
                    # name = the experiment's name (unique)
                    # artifact_location (optional) = location to store run artifacts
                # Returns: integer Id of the experiment
            return exp_id

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-

    def log_artifact_tempfile(self, name, artifact):
        """
        Using TemporaryFiles to log figures/artifacts
            Input:
                Artifact - figure (usually matplotlib)
        """
        tmpfile = NamedTemporaryFile(
            delete=False,
            prefix=name + '_',
            suffix=".png"
        )

        artifact.savefig(tmpfile)

        plt.close(artifact)

        tmpfile.close()

        mlflow.log_artifact(tmpfile.name)

        os.remove(tmpfile.name)

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-


    def logging(self, params_dictionary, metrics_dictionary=None, artifact_objs=None,
                is_aggregated=False):
        """
        Logging to mlflow():
            Inputs:
                Parameters - Dictionary
                Metrics    - Dictionary
                Artifacts  - Dictionary
        """
        metrics_dictionary = metrics_dictionary or {}
        artifact_objs = artifact_objs or {}

        #  connects to a tracking URI our case is Local
        mlflow.set_tracking_uri(self.tracking_uri)
        # Getting experiment_id
        # Does create new folder for each new experiment_id
        id = self.set_experiment_id(self.exp_folder)

        # Start mlflow():
        with mlflow.start_run(run_name=self.experiment_name, experiment_id=id):
            # TODO investigate how to not create a default experiment_id num 0.

            # Tags
            mlflow.set_tag('combined_models', is_aggregated)

            # Parameters
            for key in params_dictionary:
                mlflow.log_param(key, params_dictionary[key])

            # Metrics
            for key in metrics_dictionary:
                mlflow.log_metric(key, metrics_dictionary[key])

            # Figures / Artifacts
            for name, artifact in artifact_objs.items():
                self.log_artifact_tempfile(name, artifact)

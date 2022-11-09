import exceptions.BadInputParametersException;
import exceptions.InternalException;
import org.apache.http.auth.AuthenticationException;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import platform.Platform;

import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.nio.file.Files;
import java.nio.file.Paths;

public class Domain {

    private static final Logger logger = LogManager.getLogger(Domain.class);
    private static final String INPUT_CONFIG_FILE_PATH = "input/config.json";
    private static final String INPUT_DATA_DIRECTORY_PATH = "input/data";
    private static final String INPUT_MODEL_DIRECTORY_PATH = "input/model";
    private static final String OUTPUT_MODEL_DIRECTORY_PATH = "output/model";
    private static final String OUTPUT_INFERENCE_RESULTS_DIRECTORY_PATH = "output/inference_results";

    private final JSONArray actions;
    private final Platform platform;

    public Domain(JSONArray actions, Platform platform) {
        this.actions = actions;
        this.platform = platform;
    }

    public void run() throws BadInputParametersException, InternalException {
        for (Object actionObject: this.actions) {
            try {
                JSONObject action = (JSONObject) actionObject;
                String name = (String) action.get("name");
                switch (name) {
                    case "download_config" -> downloadConfig(action);
                    case "download_data" -> downloadData(action);
                    case "download_model" -> downloadModel(action);
                    case "create_output_model_directory" -> createOutputModelDirectory(action);
                    case "create_output_inference_results_directory" -> createOutputInferenceResultsDirectory(action);
                    default -> throw new BadInputParametersException("Action not recognized: " + name);
                }
            } catch (ClassCastException | JSONException e) {
                throw new BadInputParametersException("At least one of the actions is bad formatted: " + e.getMessage());
            }
        }
    }

    private void downloadConfig(JSONObject config) throws BadInputParametersException, InternalException {
        logger.info("Downloading config");
        platform.downloadConfig(config, Paths.get(INPUT_CONFIG_FILE_PATH));
    }

    private void downloadData(JSONObject config) throws BadInputParametersException, InternalException {
        // create input data directory
        try {
            logger.debug("Creating input data directory");
            Files.createDirectory(Paths.get(INPUT_DATA_DIRECTORY_PATH));
        } catch (IOException e) {
            throw new InternalException("Error while creating input data directory", e);
        }

        logger.info("Downloading data");
        try {
            JSONObject method = config.getJSONObject("method");
            String name = method.getString("name");
            switch (name) {
                case "input_data" -> platform.downloadInputData(method, Paths.get(INPUT_DATA_DIRECTORY_PATH));
                case "inference_input_data" -> platform.downloadInferenceInputData(method, Paths.get(INPUT_DATA_DIRECTORY_PATH));
                default -> throw new BadInputParametersException("Method for action download data not recognized: " + name);
            }
        } catch (JSONException | ClassCastException e) {
            throw new BadInputParametersException("Action download data bad formatted: " + e.getMessage());
        }

    }

    private void downloadModel(JSONObject config) throws BadInputParametersException, InternalException {
        // create input model directory
        try {
            logger.debug("Creating input model directory");
            Files.createDirectory(Paths.get(INPUT_MODEL_DIRECTORY_PATH));
        } catch (IOException e) {
            throw new InternalException("Error while creating input model directory", e);
        }

        // download model from the platform
        logger.info("Downloading model from the platform");
        this.platform.downloadModel(config, Paths.get(INPUT_MODEL_DIRECTORY_PATH));

    }

    private void createOutputModelDirectory(JSONObject config) throws InternalException {
        logger.info("Creating output model directory");
        try {
            Files.createDirectory(Paths.get(OUTPUT_MODEL_DIRECTORY_PATH));
        } catch (IOException e) {
            throw new InternalException("Error while creating the output model directory", e);
        }
    }

    private void createOutputInferenceResultsDirectory(JSONObject config) throws InternalException {
        logger.info("Creating output inference results directory");
        try {
            Files.createDirectory(Paths.get(OUTPUT_INFERENCE_RESULTS_DIRECTORY_PATH));
        } catch (IOException e) {
            throw new InternalException("Error while creating the output inference results directory", e);
        }
    }
}

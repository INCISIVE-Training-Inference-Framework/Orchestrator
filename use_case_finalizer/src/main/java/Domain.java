import exceptions.BadInputParametersException;
import exceptions.InternalException;
import org.apache.commons.io.IOUtils;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import platform.Platform;

import java.io.*;
import java.nio.charset.StandardCharsets;

import static utils.ZipCompression.zipFile;

public class Domain {

    private static final Logger logger = LogManager.getLogger(Domain.class);
    private static final String OUTPUT_MODEL_DIRECTORY_PATH = "output/model";
    private static final String OUTPUT_INFERENCE_RESULTS_DIRECTORY_PATH = "output/inference_results";
    private static final String OUTPUT_METRICS_FILE_PATH = "output/metrics.json";

    private final int jobId;
    private final String useCase;
    private final JSONArray actions;
    private final Platform platform;

    public Domain(int jobId, String useCase, JSONArray actions, Platform platform) {
        this.jobId = jobId;
        this.useCase = useCase;
        this.actions = actions;
        this.platform = platform;
    }

    public void run() throws BadInputParametersException, InternalException {
        boolean exceptionsThrown = true;
        Integer modelId = null;  // TODO refactor
        Integer inferenceResultsId = null;  // TODO idem
        try {
            for (Object actionObject: this.actions) {
                JSONObject action = (JSONObject) actionObject;
                String name = (String) action.get("name");
                switch (name) {
                    case "upload_model" -> modelId = uploadModel(action);
                    case "upload_metrics" -> modelId = uploadMetrics(action, modelId);
                    case "upload_inference_results" -> inferenceResultsId = uploadInferenceResults(action);
                    default -> throw new BadInputParametersException("Action not recognized: " + name);
                }
            }
            exceptionsThrown = false;
        } catch (ClassCastException | JSONException e) {
            throw new BadInputParametersException("At least one of the actions is bad formatted: " + e.getMessage());
        } finally {
            transmitExecutionEnd(jobId, useCase, modelId, inferenceResultsId, !exceptionsThrown);
        }
    }

    private int uploadModel(JSONObject config) throws BadInputParametersException, InternalException {
        logger.info("Uploading model");
        JSONObject metadata;
        try {
            metadata = config.getJSONObject("metadata");
        } catch (JSONException e) {
            throw new BadInputParametersException("Action upload model bad formatted: " + e.getMessage());
        }

        // compress model files
        logger.debug("Compressing model files");
        byte[] modelBytes;
        File modelDirectory = new File(OUTPUT_MODEL_DIRECTORY_PATH);
        try (ByteArrayOutputStream outputStream = new ByteArrayOutputStream()) {
            zipFile(modelDirectory, modelDirectory.getName(), outputStream);
            modelBytes = outputStream.toByteArray();
        } catch (IOException e) {
            throw new InternalException("Error while uploading the model", e);
        }

        // upload model files to the platform
        logger.debug("Uploading the model to the platform");
        return this.platform.uploadModel(metadata, modelBytes);
    }

    private int uploadMetrics(JSONObject config, Integer modelId) throws BadInputParametersException, InternalException {
        logger.info("Uploading metrics");

        JSONObject metadata;
        try {
            metadata = config.getJSONObject("metadata");
        } catch (JSONException e) {
            throw new BadInputParametersException("Action upload metrics bad formatted: " + e.getMessage());
        }

        JSONObject metrics;
        logger.debug("Reading the metrics.json file");
        try {
            InputStream is = new FileInputStream(OUTPUT_METRICS_FILE_PATH);
            String jsonTxt = IOUtils.toString(is, StandardCharsets.UTF_8);
            metrics = new JSONObject(jsonTxt);
        } catch (IOException e) {
            logger.info("WARNING: file metrics.json doesn't exist -> uploading canceled!!");
            return modelId;
        } catch (JSONException e) {
            throw new BadInputParametersException("File metrics.json bad formatted" + e.getMessage());
        }
        logger.debug("Uploading each metric");
        for (String metricName: metrics.keySet()) {
            String metricValue = String.valueOf(metrics.get(metricName));
            modelId = this.platform.uploadMetric(modelId, metadata, metricName, metricValue);
        }

        return modelId;
    }

    private int uploadInferenceResults(JSONObject config) throws BadInputParametersException, InternalException {
        logger.info("Uploading inference results");
        JSONObject metadata;
        try {
            metadata = config.getJSONObject("metadata");
        } catch (JSONException e) {
            throw new BadInputParametersException("Action upload inference results bad formatted: " + e.getMessage());
        }

        // compress inference results
        logger.debug("Compressing inference results");
        byte[] inferenceResultsBytes;
        File modelDirectory = new File(OUTPUT_INFERENCE_RESULTS_DIRECTORY_PATH);
        try (ByteArrayOutputStream outputStream = new ByteArrayOutputStream()) {
            zipFile(modelDirectory, modelDirectory.getName(), outputStream);
            inferenceResultsBytes = outputStream.toByteArray();
        } catch (IOException e) {
            throw new InternalException("Error while compressing inference results", e);
        }

        // upload model files to the platform
        logger.debug("Uploading inference results to the platform");
        return this.platform.uploadInferenceResults(metadata, inferenceResultsBytes);
    }

    private void transmitExecutionEnd(int jobId, String useCase, Integer modelId, Integer inferenceResultsId, boolean success) throws BadInputParametersException, InternalException {
        logger.debug("Transmitting execution end to the platform");
        this.platform.transmitExecutionEnd(jobId, useCase, modelId, inferenceResultsId, success);
    }
}

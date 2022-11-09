package platform.types;

import config.EnvironmentVariable;
import config.EnvironmentVariableType;
import exceptions.BadConfigurationException;
import exceptions.BadInputParametersException;
import exceptions.InternalException;
import org.json.JSONException;
import org.json.JSONObject;
import platform.Platform;
import utils.HttpCalls;

import java.io.IOException;
import java.util.List;
import java.util.Map;

public class Incisive implements Platform {

    private static final String TRAINING_FROM_SCRATCH = "training_from_scratch";
    private static final String TRAINING_FROM_PRETRAINED_MODEL = "training_from_pretrained_model";
    private static final String EVALUATING_FROM_PRETRAINED_MODEL = "evaluating_from_pretrained_model";
    private static final String INFERENCING_FROM_PRETRAINED_MODEL = "inferencing_from_pretrained_model";
    public static List<EnvironmentVariable> getEnvironmentVariables() {
        return List.of(
                new EnvironmentVariable("MAAS_SERVICE_HOSTNAME", EnvironmentVariableType.STRING),
                new EnvironmentVariable("ORCHESTRATOR_SERVICE_HOSTNAME", EnvironmentVariableType.STRING)
        );
    }

    private final String maasHostname;
    private final String orchestratorHostname;

    public Incisive(Map<String, Object> config) throws BadConfigurationException {
        this.maasHostname = (String) config.get("MAAS_SERVICE_HOSTNAME");
        this.orchestratorHostname = (String) config.get("ORCHESTRATOR_SERVICE_HOSTNAME");
    }

    @Override
    public int uploadModel(JSONObject metadata, byte[] model) throws InternalException {
        try {
            String url = "http://" + this.maasHostname + "/api/models/update_or_create/";
            HttpCalls.HttpResponse httpResponse = HttpCalls.multipartJsonAndFileUpload(url, metadata, "model_files", model);

            if (httpResponse.getStatusCode() != 201 && httpResponse.getStatusCode() != 200) {
                throw new InternalException("Error while uploading model to the MaaS. Wrong status code: " + httpResponse.getStatusCode() + " " + httpResponse.getResponseContents(), null);
            }
            JSONObject responseJson = new JSONObject(httpResponse.getResponseContents());
            return responseJson.getInt("id");

        } catch (JSONException | IOException e) {
            throw new InternalException("Error while uploading model to the MaaS", e);
        }
    }



    @Override
    public int uploadMetric(Integer modelId, JSONObject metadata, String metricName, String metricValue) throws BadInputParametersException, InternalException {
        if (!metadata.has("model") && modelId == null) throw new BadInputParametersException("No model identifier specified for uploading the metrics");
        else if (modelId != null) {
            metadata.put("model", modelId);
        }

        metadata.put("name", metricName);
        metadata.put("value", metricValue);

        String url = "http://" + this.maasHostname + "/api/metrics/update_or_create/";
        try {
            HttpCalls.HttpResponse httpResponse = HttpCalls.jsonUpload(url, metadata, "POST");

            if (httpResponse.getStatusCode() != 201 && httpResponse.getStatusCode() != 200) {
                throw new InternalException("Error while uploading metric "+metricName+" to the MaaS. Wrong status code: " + httpResponse.getStatusCode() + " " + httpResponse.getResponseContents(), null);
            }

        } catch (IOException e) {
            throw new InternalException("Error while uploading metric to the MaaS", e);
        }

        return metadata.getInt("model");
    }

    @Override
    public int uploadInferenceResults(JSONObject metadata, byte[] inferenceResults) throws InternalException {
        String url = "http://" + this.maasHostname + "/api/inference_results/";
        try {
            HttpCalls.HttpResponse httpResponse = HttpCalls.multipartJsonAndFileUpload(url, metadata, "result_files", inferenceResults);

            if (httpResponse.getStatusCode() != 201) {
                throw new InternalException("Error while uploading inference results to the MaaS. Wrong status code: " + httpResponse.getStatusCode() + " " + httpResponse.getResponseContents(), null);
            }

            JSONObject responseJson = new JSONObject(httpResponse.getResponseContents());
            return responseJson.getInt("id");

        } catch (JSONException | IOException e) {
            throw new InternalException("Error while uploading inference results to the MaaS", e);
        }
    }

    @Override
    public void transmitExecutionEnd(int jobId, String useCase, Integer modelId, Integer inferenceResultsId, boolean success) throws BadInputParametersException, InternalException {
        String parsedSuccess;
        String result = null;
        if (success) {
            parsedSuccess = "Succeeded";
            switch (useCase) {
                case TRAINING_FROM_SCRATCH, TRAINING_FROM_PRETRAINED_MODEL -> {
                    if (modelId == null)
                        throw new BadInputParametersException("Model id is needed for transmitting the end of the execution");
                    result = "http://" + this.maasHostname + "/api/models/" + modelId + "/download_model_files/";
                }
                case EVALUATING_FROM_PRETRAINED_MODEL -> {
                    if (modelId == null)
                        throw new BadInputParametersException("Model id is needed for transmitting the end of the execution");
                    result = "http://" + this.maasHostname + "/api/metrics/?model=" + modelId;
                }
                case INFERENCING_FROM_PRETRAINED_MODEL -> {
                    if (inferenceResultsId == null)
                        throw new BadInputParametersException("Inference results id is needed for transmitting the end of the execution");
                    result = "http://" + this.maasHostname + "/api/inference_results/" + inferenceResultsId + "/";
                }
                default -> throw new BadInputParametersException("Unrecognized use case: " + useCase);
            }
        } else parsedSuccess = "Failed";

        JSONObject metadata = new JSONObject();
        metadata.put("status", parsedSuccess);
        if (result != null) metadata.put("result", result);

        try {
            String url = "http://" + this.orchestratorHostname + "/api/jobs/" + jobId + "/ended_job_execution/";
            HttpCalls.HttpResponse httpResponse = HttpCalls.jsonUpload(url, metadata, "PATCH");

            if (httpResponse.getStatusCode() != 200) {
                throw new InternalException("Error while updating the end of the execution to the Orchestrator. Wrong status code: " + httpResponse.getStatusCode() + " " + httpResponse.getResponseContents(), null);
            }

        } catch (IOException e) {
            throw new InternalException("Error while updating the end of the execution to the Orchestrator", e);
        }
    }
}

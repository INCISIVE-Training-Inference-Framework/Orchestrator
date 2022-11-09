package platform;

import exceptions.BadInputParametersException;
import exceptions.InternalException;
import org.json.JSONObject;

public interface Platform {

    int uploadModel(JSONObject metadata, byte[] model) throws InternalException;

    int uploadMetric(Integer modelId, JSONObject metadata, String metricName, String metricValue) throws BadInputParametersException, InternalException;

    int uploadInferenceResults(JSONObject metadata, byte[] inferenceResults) throws InternalException;

    void transmitExecutionEnd(int jobId, String useCase, Integer modelId, Integer inferenceResultsId, boolean success) throws BadInputParametersException, InternalException;

}

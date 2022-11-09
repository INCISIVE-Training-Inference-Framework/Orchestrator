package platform.types;

import exceptions.BadInputParametersException;
import exceptions.InternalException;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.json.JSONObject;
import platform.Platform;

public class Dummy implements Platform {

    private static final Logger logger = LogManager.getLogger(Dummy.class);

    private byte[] model;
    private String metric;

    @Override
    public int uploadModel(JSONObject metadata, byte[] model) throws InternalException {
        logger.debug("uploadModel method called");
        this.model = model;
        return 1;
    }

    @Override
    public int uploadMetric(Integer modelId, JSONObject metadata, String metricName, String metricValue) throws BadInputParametersException, InternalException {
        logger.debug("uploadMetric method called");
        this.metric = metricName + metricValue;
        return 1;
    }

    @Override
    public int uploadInferenceResults(JSONObject metadata, byte[] inferenceResults) throws InternalException {
        logger.debug("uploadInferenceResults method called");
        return 1;
    }

    @Override
    public void transmitExecutionEnd(int jobId, String useCase, Integer modelId, Integer inferenceResultsId, boolean success) throws BadInputParametersException, InternalException {
        logger.debug("transmitExecutionEnd method called");
    }

    public byte[] getModel() {
        return model;
    }

    public String getMetric() { return metric;}
}

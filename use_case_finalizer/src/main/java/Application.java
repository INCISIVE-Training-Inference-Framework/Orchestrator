import config.EnvironmentVariable;
import exceptions.BadConfigurationException;
import exceptions.BadInputParametersException;
import exceptions.InternalException;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import platform.types.Incisive;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Application {

    private static final Logger logger = LogManager.getLogger(Application.class);

    private record InputParameters(int jobId, String useCase, JSONArray actions) {

        public int getJobId() {
            return jobId;
        }

        public String getUseCase() {
            return useCase;
        }

        public JSONArray getActions() {
            return actions;
        }

        @Override
        public String toString() {
            return "InputParameters{" +
                    "jobId=" + jobId +
                    ", useCase='" + useCase + '\'' +
                    ", actions=" + actions.toString(2) +
                    '}';
        }
    }

    public static void main(String[] args) {
        try {
            // parse input parameters
            InputParameters inputParameters = parseInputParameters(args);
            logger.info(inputParameters);

            // run main application
            Map<String, Object> config = loadEnvironmentVariables(Incisive.getEnvironmentVariables());
            Incisive incisive = new Incisive(config);
            Domain domain = new Domain(inputParameters.getJobId(), inputParameters.getUseCase(), inputParameters.getActions(), incisive);
            domain.run();
        } catch (BadConfigurationException | BadInputParametersException e) {
            logger.error(e);
            System.exit(1);
        } catch (InternalException e) {
            printException(e);
            System.exit(1);
        }
    }

    private static InputParameters parseInputParameters(String[] args) throws BadInputParametersException {
        if (args.length != 3) throw new BadInputParametersException(
                "There should be 3 input parameters:" +
                        "-> the job identifier " +
                        "-> the use case " +
                        "-> JSON object with the array of actions to perform");

        int jobId;
        try {
            jobId = Integer.parseInt(args[0]);
        } catch (ClassCastException e) {
            throw new BadInputParametersException("The job id is not valid: " + e.getMessage());
        }

        String use_case = args[1];

        JSONObject inputJson;
        try {
            inputJson = new JSONObject(args[2]);
        } catch (JSONException e) {
            throw new BadInputParametersException("The input JSON object is not a valid JSON: " + e.getMessage());
        }

        JSONArray actions;
        try {
            actions = (JSONArray) inputJson.get("actions");
        } catch (JSONException e) {
            throw new BadInputParametersException("The input JSON object does not contain a JSON array with the actions to perform");
        }  // TODO check what happens if it is a JSON Array

        return new InputParameters(jobId, use_case, actions);
    }

    private static Map<String, Object> loadEnvironmentVariables(List<EnvironmentVariable> environmentVariables) throws BadConfigurationException {
        Map<String, Object> config = new HashMap<>();
        for (EnvironmentVariable environmentVariable: environmentVariables) {
            config.put(environmentVariable.name, environmentVariable.load());
        }
        return config;
    }

    private static void printException(InternalException e) {
        logger.error(e.getMessage());
        if (e.getException() != null) {
            logger.error(e.getException().getMessage());
            e.getException().printStackTrace();
        }
    }
}

package platform.types;

import config.EnvironmentVariable;
import config.EnvironmentVariableType;
import exceptions.BadInputParametersException;
import exceptions.InternalException;
import org.apache.http.HttpEntity;

import org.apache.http.auth.AuthenticationException;
import org.apache.http.auth.UsernamePasswordCredentials;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.auth.BasicScheme;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import platform.Platform;
import utils.ZipCompression;

import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;

public class Incisive implements Platform {

    public static List<EnvironmentVariable> getEnvironmentVariables() {
        List<EnvironmentVariable> environmentVariables = new ArrayList<>();
        environmentVariables.add(new EnvironmentVariable("MAAS_SERVICE_HOSTNAME", EnvironmentVariableType.STRING));
        environmentVariables.add(new EnvironmentVariable("ORCHESTRATOR_SERVICE_HOSTNAME", EnvironmentVariableType.STRING));
        environmentVariables.add(new EnvironmentVariable("PACS_SERVICE_HOSTNAME", EnvironmentVariableType.STRING, "incisive-dp-pacs-service:8042"));
        environmentVariables.add(new EnvironmentVariable("FHIR_SERVICE_HOSTNAME", EnvironmentVariableType.STRING, "incisive-dp-fhir-service:9080"));
        return environmentVariables;
    }

    private static final Logger logger = LogManager.getLogger(Incisive.class);
    private final String maasServiceHostname;
    private final String orchestratorServiceHostname;
    private final String pacsServiceHostname;
    private final String fhirServiceHostname;

    public Incisive(Map<String, Object> config) {
        this.maasServiceHostname = (String) config.get("MAAS_SERVICE_HOSTNAME");
        this.orchestratorServiceHostname = (String) config.get("ORCHESTRATOR_SERVICE_HOSTNAME");
        this.pacsServiceHostname = (String) config.get("PACS_SERVICE_HOSTNAME");
        this.fhirServiceHostname = (String) config.get("FHIR_SERVICE_HOSTNAME");
    }

    @Override
    public void downloadConfig(JSONObject config, Path filePath) throws BadInputParametersException, InternalException {
        try (FileOutputStream outputStream = new FileOutputStream(filePath.toString())) {
            String jobId = String.valueOf(config.getInt("job_id"));
            String url = "http://" + this.orchestratorServiceHostname + "/api/jobs/" + jobId + "/download_ai_engine_config/";
            downloadFile(url, outputStream);
        } catch (ClassCastException | JSONException e) {
            throw new BadInputParametersException("Action download config is bad formatted: " + e.getMessage());
        } catch (IOException e) {
            throw new InternalException("Error while downloading the config from Orchestrator", e);
        }
    }

    @Override
    public void downloadModel(JSONObject config, Path directoryPath) throws BadInputParametersException, InternalException {
        try (ByteArrayOutputStream outputStream = new ByteArrayOutputStream()) {
            // download model files
            String modelId = String.valueOf(config.getInt("model_id"));
            String url = "http://" + this.maasServiceHostname + "/api/models/" + modelId + "/download_model_files/";
            downloadFile(url, outputStream);

            // uncompress the model files and put them inside the directory
            ZipCompression.unZipFile(new ByteArrayInputStream(outputStream.toByteArray()), directoryPath);

        } catch (ClassCastException | JSONException e) {
            throw new BadInputParametersException("Action download model is bad formatted: " + e.getMessage());
        } catch (IOException e) {
            throw new InternalException("Error while downloading model files from MaaS", e);
        }
    }


    @Override
    public void downloadInputData(JSONObject config, Path directoryPath) throws InternalException {
        CloseableHttpClient client = HttpClients.createDefault();

        // Creating dicom and fhir directory
        Path dicomDirectoryPath = directoryPath.resolve("dicom");
        Path fhirDirectoryPath = directoryPath.resolve("fhir");
        try {
            Files.createDirectory(dicomDirectoryPath);
            Files.createDirectory(fhirDirectoryPath);
        } catch (IOException e) {
            throw new InternalException("Error while creating dicom and fhir directory", e);
        }

        // Download dicom and metadata for each patient
        JSONArray patients = config.getJSONArray("data_partner_patients");
        logger.debug("Patients:" + patients);
        for (Object patient: patients) {
            downloadDicomForPatient(client, (String) patient, dicomDirectoryPath);
            downloadMetadataForPatient(client, (String) patient, fhirDirectoryPath);
        }
        File f1 = new File(dicomDirectoryPath.toString());
        File f2 = new File(fhirDirectoryPath.toString());
        logger.debug("Files dicom: " + Arrays.toString(f1.list()));
        logger.debug("Files fhir: " + Arrays.toString(f2.list()));
    }


    @Override
    public void downloadInferenceInputData(JSONObject config, Path directoryPath) throws BadInputParametersException, InternalException {
        try (ByteArrayOutputStream outputStream = new ByteArrayOutputStream()) {
            // download model files
            String jobId = String.valueOf(config.getInt("job_id"));
            String url = "http://" + this.orchestratorServiceHostname + "/api/jobs/" + jobId + "/download_input_data_files/";
            downloadFile(url, outputStream);

            // uncompress the model files and put them inside the directory
            ZipCompression.unZipFile(new ByteArrayInputStream(outputStream.toByteArray()), directoryPath);

        } catch (ClassCastException | JSONException e) {
            throw new BadInputParametersException("Action download input inference data is bad formatted: " + e.getMessage());
        } catch (IOException e) {
            throw new InternalException("Error while downloading input inference data files from MaaS", e);
        }
    }

    private void downloadFile(String url, OutputStream outputStream) throws IOException {
        // TODO add method to work in disk for heavy models
        try (BufferedInputStream in = new BufferedInputStream(new URL(url).openStream())) {
            byte[] dataBuffer = new byte[1024];
            int bytesRead;
            while ((bytesRead = in.read(dataBuffer, 0, 1024)) != -1) {
                outputStream.write(dataBuffer, 0, bytesRead);
            }
        }
    }

    private JSONArray getInstancesForPatient(CloseableHttpClient client, UsernamePasswordCredentials credentials,
                                             String patient) throws InternalException {
        String pacsUrl = "http://" + this.pacsServiceHostname + "/tools/find";
        HttpPost httpPost = new HttpPost(pacsUrl);
        String body = "{ \"Level\" : \"Instances\", \"Query\" : { \"PatientID\" : \"" + patient + "\" }}";
        try {
            httpPost.setEntity(new StringEntity(body));
            httpPost.setHeader("Accept", "application/json");
            httpPost.setHeader("Content-type", "application/json");
            httpPost.addHeader(new BasicScheme().authenticate(credentials, httpPost, null));
        } catch (UnsupportedEncodingException | AuthenticationException e) {
            throw new InternalException("Error while getting instances for patient "+patient, e);
        }

        String responseContent = "";
        try (CloseableHttpResponse httpResponse = client.execute(httpPost)) {
            HttpEntity entity = httpResponse.getEntity();
            if (entity != null) {
                try (InputStream inputStream = httpResponse.getEntity().getContent()) {
                    responseContent = new String(inputStream.readAllBytes(), StandardCharsets.UTF_8);
                }
            }
        } catch (IOException e) {
            throw new InternalException("Error while retrieving patient \""+patient+"\" instances", e);
        }
        return new JSONArray(responseContent);
    }

    private void downloadDicomForPatient(CloseableHttpClient client, String patient, Path directoryPath)
            throws InternalException {
        UsernamePasswordCredentials credentials = new UsernamePasswordCredentials("pacsuser","incisive");

        JSONArray instances = getInstancesForPatient(client, credentials, patient);
        logger.debug("Instances for "+patient+": "+instances);
        for (Object instance: instances) {
            String instanceUrl = "http://" + this.pacsServiceHostname + "/instances/" + instance + "/file";
            HttpGet httpGet = new HttpGet(instanceUrl);
            try {
                httpGet.addHeader(new BasicScheme().authenticate(credentials, httpGet, null));
            } catch (AuthenticationException e) {
                throw new InternalException("Error while authentification for PACS DICOM downloading", e);
            }

            try (CloseableHttpResponse httpResponse = client.execute(httpGet)) {
                HttpEntity entity = httpResponse.getEntity();
                if (entity != null) {
                    String dicomFile = directoryPath.resolve(patient+"-"+instance+".dcm").toString();
                    try (FileOutputStream outstream = new FileOutputStream(dicomFile)) {
                        entity.writeTo(outstream);
                    } catch (IOException e) {
                        throw new InternalException("Error while writing data into de dicom files", e);
                    }
                }
            } catch (IOException e) {
                throw new InternalException("Error while downloading data from PACS for the input", e);
            }
        }
    }

    private void downloadMetadataForPatient(CloseableHttpClient client, String patient, Path directoryPath) throws InternalException {
        UsernamePasswordCredentials credentials = new UsernamePasswordCredentials("fhiruser","incisive");
        Map<String, String> urls = new HashMap<>();
        urls.put("procedure", "http://"+this.fhirServiceHostname+"/fhir-server/api/v4/Procedure?subject="+patient+"&_pretty=true");
        urls.put("condition", "http://"+this.fhirServiceHostname+"/fhir-server/api/v4/Condition?subject="+patient+"&_pretty=true");
        urls.put("observation", "http://"+this.fhirServiceHostname+"/fhir-server/api/v4/Observation?subject="+patient+"&_pretty=true");
        urls.put("general_info", "http://"+this.fhirServiceHostname+"/fhir-server/api/v4/Patient/"+patient+"?_pretty=true");

        for (String metadata: urls.keySet()) {
            HttpGet httpGet = new HttpGet(urls.get(metadata));
            try {
                httpGet.addHeader(new BasicScheme().authenticate(credentials, httpGet, null));
            } catch (AuthenticationException e) {
                throw new InternalException("Error while authentification for FHIR metadata downloading", e);
            }
            try (CloseableHttpResponse httpResponse = client.execute(httpGet)) {
                HttpEntity entity = httpResponse.getEntity();
                if (entity != null) {
                    try (InputStream inputStream = entity.getContent()) {
                        String responseContent = new String(inputStream.readAllBytes(), StandardCharsets.UTF_8);
                        JSONObject responseJSON = new JSONObject(responseContent);
                        String resourceType = responseJSON.getString("resourceType");
                        if ((resourceType.equals("Bundle") && responseJSON.getInt("total") <= 0)
                            || resourceType.equals("OperationOutcome")) {
                            logger.debug("WARNING: while fetching patient in FHIR: 0 results of "+metadata+
                                    " for patient "+patient);
                        } else {
                            String metadataFile = directoryPath.resolve(patient + "-" + metadata + ".json").toString();
                            try (FileOutputStream outstream = new FileOutputStream(metadataFile)) {
                                entity.writeTo(outstream);
                            } catch (IOException e) {
                                throw new InternalException("Error while writing metadata " + metadata + " into de json file", e);
                            }
                        }
                    }
                }
            } catch (IOException | InternalException e) {
                throw new InternalException("Error while downloading metadata " + metadata + " from FHIR for the input", e);
            }
        }
    }
}

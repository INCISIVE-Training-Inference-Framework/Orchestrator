import com.github.tomakehurst.wiremock.junit.WireMockRule;
import exceptions.BadInputParametersException;
import exceptions.InternalException;
import org.apache.commons.io.FileUtils;
import org.json.JSONArray;
import org.json.JSONObject;
import org.junit.*;
import platform.types.Incisive;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;
import java.util.stream.Collectors;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

import static com.github.tomakehurst.wiremock.client.WireMock.*;
import static org.junit.Assert.*;

public class TestDownloadModel {

    @Rule
    public WireMockRule wireMockRule = new WireMockRule(8000);
    public JSONObject downloadModelAction;
    public static ByteArrayOutputStream byteArrayOutputStream;

    @BeforeClass
    public static void beforeClass() throws Exception {
        // delete dummy files
        Files.delete(Paths.get("input/empty.txt"));
        Files.delete(Paths.get("output/empty.txt"));

        // create dummy zip compressed file
        Path modelFilePath = Paths.get("src/test/resources/model/model.pt");
        Path configModelFilePath = Paths.get("src/test/resources/model/model_config.json");
        Files.createDirectory(Paths.get("src/test/resources/model"));
        Files.createFile(modelFilePath);
        Files.createFile(configModelFilePath);
        List<String> lines = Arrays.asList("test model content 1", "test model content 2");
        Files.write(modelFilePath, lines, StandardCharsets.UTF_8);
        lines = List.of("{\"test\": \"dummy_json\"}");
        Files.write(configModelFilePath, lines, StandardCharsets.UTF_8);
        byteArrayOutputStream = new ByteArrayOutputStream();
        zipFile(new File("src/test/resources/model"), "model", byteArrayOutputStream);
    }

    @Before
    public void before() throws Exception {
        // create config
        downloadModelAction = new JSONObject(
                "{" +
                        "\"name\": \"download_model\", " +
                        "\"model_id\": 1" +
                        "}"
        );
    }

    @After
    public void after() throws Exception {
        // clean test environment
        FileUtils.cleanDirectory(new File("src/test/resources"));
        FileUtils.cleanDirectory(new File("input"));
        FileUtils.cleanDirectory(new File("output"));
    }

    @AfterClass
    public static void afterClass() throws Exception {
        // create dummy files
        Files.createFile(Paths.get("input/empty.txt"));
        Files.createFile(Paths.get("output/empty.txt"));
        Files.createFile(Paths.get("src/test/resources/empty.txt"));

        // close byte array
        byteArrayOutputStream.close();
    }

    @Test
    public void downloadModelSuccess() throws Exception {
        // create mock
        stubFor(get(urlEqualTo("/api/models/1/download_model_files/"))
                .willReturn(aResponse().withBody(byteArrayOutputStream.toByteArray())));

        // run domain
        JSONArray actions = new JSONArray();
        actions.put(downloadModelAction);
        Map<String, Object> incisiveConfig = new HashMap<>();
        incisiveConfig.put("MAAS_SERVICE_HOSTNAME", "localhost:8000");
        Domain domain = new Domain(actions, new Incisive(incisiveConfig));
        domain.run();

        // assure files are ok
        List<String> directoryFiles = listDirectoryFiles("input");
        assertEquals(Arrays.asList("model", "model.pt", "model_config.json"), directoryFiles);
        directoryFiles = listDirectoryFiles("output");
        assertEquals(new ArrayList<>(), directoryFiles);

        // assure model files contents are ok
        List<String> lines = Files.lines(Paths.get("input/model/model.pt"), StandardCharsets.UTF_8).collect(Collectors.toList());
        assertEquals(Arrays.asList("test model content 1", "test model content 2"), lines);
        lines = Files.lines(Paths.get("input/model/model_config.json"), StandardCharsets.UTF_8).collect(Collectors.toList());
        assertEquals(List.of("{\"test\": \"dummy_json\"}"), lines);
    }

    @Test
    public void downloadModelFailed() throws Exception {
        downloadModelAction = new JSONObject(
                "{" +
                        "\"name\": \"download_model\""+
                        "}"
        );

        Exception exception = assertThrows(BadInputParametersException.class, () -> {
            JSONArray actions = new JSONArray();
            actions.put(downloadModelAction);
            Map<String, Object> incisiveConfig = new HashMap<>();
            incisiveConfig.put("MAAS_SERVICE_HOSTNAME", "localhost:8000");
            Domain domain = new Domain(actions, new Incisive(incisiveConfig));
            domain.run();
        });

        String expectedMessage = "Action download model is bad formatted";
        assertTrue(exception.getMessage().contains(expectedMessage));
    }

    @Test
    public void downloadModelBadFormatted() throws Exception {
        // create mock
        stubFor(get(urlEqualTo("/api/models/1/download_model_files/"))
                .willReturn(aResponse().withStatus(400).withBody("")));

        Exception exception = assertThrows(InternalException.class, () -> {
            JSONArray actions = new JSONArray();
            actions.put(downloadModelAction);
            Map<String, Object> incisiveConfig = new HashMap<>();
            incisiveConfig.put("MAAS_SERVICE_HOSTNAME", "localhost:8000");
            Domain domain = new Domain(actions, new Incisive(incisiveConfig));
            domain.run();
        });

        String expectedMessage = "Error while downloading model files from MaaS";
        assertTrue(exception.getMessage().contains(expectedMessage));
    }

    private static List<String> listDirectoryFiles(String dir) throws IOException {
        List<String> directoryFiles = new ArrayList<>();
        try (DirectoryStream<Path> stream = Files.newDirectoryStream(Paths.get(dir))) {
            for (Path path : stream) {
                if (!Files.isDirectory(path)) {
                    directoryFiles.add(path.getFileName().toString());
                } else {
                    directoryFiles.add(path.getFileName().toString());
                    directoryFiles.addAll(listDirectoryFiles(path.toString()));
                }
            }
        }
        return directoryFiles;
    }

    public static void zipFile(File fileToZip, String fileName, OutputStream outputStream) throws IOException {
        try(ZipOutputStream zipOut = new ZipOutputStream(outputStream)) {
            zipFileRecursive(fileToZip, fileName, zipOut);
        }
    }
    private static void zipFileRecursive(File fileToZip, String fileName, ZipOutputStream zipOut) throws IOException {
        if (fileToZip.isHidden()) {
            return;
        }
        if (fileToZip.isDirectory()) {
            if (fileName.endsWith("/")) {
                zipOut.putNextEntry(new ZipEntry(fileName));
                zipOut.closeEntry();
            } else {
                zipOut.putNextEntry(new ZipEntry(fileName + "/"));
                zipOut.closeEntry();
            }
            final File[] children = fileToZip.listFiles();
            for (final File childFile : children) {
                zipFileRecursive(childFile, fileName + "/" + childFile.getName(), zipOut);
            }
            return;
        }
        try(FileInputStream fis = new FileInputStream(fileToZip)) {
            ZipEntry zipEntry = new ZipEntry(fileName);
            zipOut.putNextEntry(zipEntry);
            byte[] bytes = new byte[1024];
            int length;
            while ((length = fis.read(bytes)) >= 0) {
                zipOut.write(bytes, 0, length);
            }
        }
    }

}

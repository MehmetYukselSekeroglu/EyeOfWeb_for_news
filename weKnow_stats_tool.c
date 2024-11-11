#include <stdio.h>
#include <stdlib.h>
#include <postgresql/libpq-fe.h>
#include <string.h>
#include <cjson/cJSON.h>

#ifdef _WIN32
    #define CONFIG_FILE "config\\config.json"
#else
    #define CONFIG_FILE "config/config.json"
#endif


#define DEFAULT_BUFFER_SIZE 5000

void removeNewLine(char* str){
    size_t length = strlen(str);

    if (length > 0 && str[length -1] == '\n'){
        str[length-1] = '\0';
    }
}


const char **LoadConfigJson(void){
    const char **config = malloc(4 * sizeof(char*));

    FILE *ConfigFile = fopen(CONFIG_FILE, "r");

    if (ConfigFile == NULL){
        fprintf(stderr, "[ERROR]: Failed to open config file: %s", CONFIG_FILE);
        return NULL;

    }

    char buffer[DEFAULT_BUFFER_SIZE];
    int len = fread(buffer, 1, sizeof(buffer), ConfigFile);

    fclose(ConfigFile);

    cJSON *JsonData = cJSON_Parse(buffer);

    if (JsonData == NULL){
        fprintf(stderr, "[ERROR]: Failed to parse config file (format json): %s", CONFIG_FILE);
        cJSON_Delete(JsonData);
        return NULL;
    
    }
    cJSON *databaseConfig = cJSON_GetObjectItem(JsonData, "database_config");

    if (databaseConfig == NULL){
        return NULL;
    }

    cJSON *database_name = cJSON_GetObjectItem(databaseConfig, "database");
    cJSON *database_username = cJSON_GetObjectItem(databaseConfig, "user");
    cJSON *database_password = cJSON_GetObjectItem(databaseConfig, "password");
    cJSON *database_address  = cJSON_GetObjectItem(databaseConfig, "host");


    if (database_address == NULL || database_name == NULL || database_username == NULL){
        return NULL;
    }


    const char *address = cJSON_GetStringValue(database_address);
    const char *name = cJSON_GetStringValue(database_name);
    const char *username = cJSON_GetStringValue(database_username);
    const char *password = cJSON_GetStringValue(database_password);


    config[0]=strdup(address);
    config[1]=strdup(name);
    config[2]=strdup(username);
    config[3]=strdup(password);

    cJSON_Delete(JsonData);
    return config;

}




const char **LoadConfig(void){
    const char **config = malloc(4 * sizeof(char*));

    FILE *TargetFile;
    TargetFile = fopen("config.cnf", "r");

    if (TargetFile == NULL){
        fprintf(stderr,"[-] Failed to open file: config.cnf \n");
        return NULL;
    }

    for (int i; i < 4 ; i++){
        config[i] =  malloc(1000 * sizeof(char));

        if (config[i] == NULL){
            fprintf(stderr, "[-] Memory allocation failed!\n");
            return NULL;
        }
    }

    fgets((char*) config[0], 1000, TargetFile);
    fgets((char*) config[1], 1000, TargetFile);
    fgets((char*) config[2], 1000, TargetFile);
    fgets((char*) config[3], 1000, TargetFile);

    removeNewLine((char*)config[0]);
    removeNewLine((char*)config[1]);
    removeNewLine((char*)config[2]);
    removeNewLine((char*)config[3]);




    return config;
}


PGconn* ConnectDatabase(const char* host, const char* db_name, const char* username, const char* password) {
    PGconn *Connection; 
    
    char buffer[1000];
    sprintf(buffer, "host='%s' dbname='%s' user='%s' password='%s'", host,db_name, username,password);
    
    Connection = PQconnectdb(buffer);
    
    
    if (PQstatus(Connection) != CONNECTION_OK){
        fprintf(stderr,"Failed to connect database: %s", PQerrorMessage(Connection));
        PQfinish(Connection);
        return NULL;
    }



    return Connection;
}


void showHelp(void){
    fprintf(stdout,"[WeKnow] STATS TOOL HELP PAGE\t\n\n");
    fprintf(stdout,"[--dump-domain]: Dump all domain on screen\t\n");
    fprintf(stdout,"[--dump-phone]: Dump all phone numbers on screen\t\n");
    fprintf(stdout,"[--dump-email]: Dump all e-mail address on screen\t\n");
    fprintf(stdout,"[--dump-path]: Dump all url path on screen\t\n");
}


int main(int argc, char const *argv[]){


    if (argc != 2){
        fprintf(stderr, "[ERROR]: Invalid Usage Visit --help\t.");
        exit(1);
    }

    const char *SELECTION = argv[1];


    if (strcmp(SELECTION, "--help") == 0){
        showHelp();
        exit(0);
    }





    fprintf(stdout, "[INFO]: Loading config ...\t\n");
    const char **CONNECTION_CONFIG = LoadConfigJson();



    if (strcmp(SELECTION, "--dump-config") == 0){
        for (int i = 0 ; i < 4; i++){
            fprintf(stdout, "[+] Config İndex: %d ||| Val: %s\n", i, CONNECTION_CONFIG[i]);
        }
        return 0;
    }


    fprintf(stdout, "[INFO]: Connection to database ....\n");

    PGconn *Connection; 
    PGresult *Results;

    char buffer[1000];
    sprintf(buffer, "host='%s' dbname='%s' user='%s' password='%s'", CONNECTION_CONFIG[0],CONNECTION_CONFIG[1], CONNECTION_CONFIG[2],CONNECTION_CONFIG[3]);
    


    Connection = PQconnectdb(buffer);
    

    
    if (PQstatus(Connection) != CONNECTION_OK || Connection == NULL){
        fprintf(stderr,"[ERROR]: Failed to connect database: %s", PQerrorMessage(Connection));
        PQfinish(Connection);
        return -1;
    }

    static char *STATIC_SQL_COMMAND;
    int rows;
    int columns;

    if (strcmp(SELECTION, "--count-all") == 0){
        STATIC_SQL_COMMAND = "SELECT COUNT(*) FROM \"ImageBasedMain\"";
        Results = PQexec(Connection, STATIC_SQL_COMMAND);
    
    
        if (PQresultStatus(Results) != PGRES_TUPLES_OK){
            fprintf(stderr, "[ERROR]: Sorgulama hatası: %s", PQerrorMessage(Connection));
            PQclear(Results);
            PQfinish(Connection);
            exit(1);
        }
    
        rows = PQntuples(Results);
        columns = PQnfields(Results);
    
    
        if (rows > 0 && columns > 0){
            fprintf(stdout,"[*] Query: ImageBasedMain => %s \n", PQgetvalue(Results, 0, 0));
        }else{
            fprintf(stdout, "[INFO] No Results Found ....");
        }

        STATIC_SQL_COMMAND = "SELECT COUNT(*) FROM \"ImageHashID\"";
        
        Results = PQexec(Connection, STATIC_SQL_COMMAND);

        rows = PQntuples(Results);
        columns = PQnfields(Results);

        if (rows > 0 && columns > 0){
            fprintf(stdout,"[*] Query: ImageHashID => %s \n", PQgetvalue(Results, 0, 0));
        }else{
            fprintf(stdout, "[-] No Results Found ....");
        }



        STATIC_SQL_COMMAND = "SELECT COUNT(*) FROM \"FaceStorageID\"";

        Results = PQexec(Connection, STATIC_SQL_COMMAND);

        rows = PQntuples(Results);
        columns = PQnfields(Results);

        if (rows > 0 && columns > 0){
            fprintf(stdout,"[*] Query: FaceStorageID => %s \n", PQgetvalue(Results, 0, 0));
        }else{
            fprintf(stdout, "[-] No Results Found ....");
        }
    }else if(strcmp(SELECTION, "--dump-domain") == 0){
        STATIC_SQL_COMMAND = "SELECT * FROM \"BaseDomainID\"";

        Results = PQexec(Connection, STATIC_SQL_COMMAND);




        rows = PQntuples(Results);
        columns = PQnfields(Results);

        fprintf(stdout, "ID\tDOMAIN\n");
        for (int i = 0 ; i < rows; i++){
            for (int j = 0; j < columns ; j++){
                fprintf(stdout, "%s \t", PQgetvalue(Results,i,j));
            }
            fprintf(stdout, "\n");
        }
    }else if(strcmp(SELECTION, "--dump-email") == 0){
        STATIC_SQL_COMMAND = "SELECT * FROM \"EmailAddressID\" ";
        Results = PQexec(Connection, STATIC_SQL_COMMAND);

        rows = PQntuples(Results);
        columns = PQnfields(Results);



        fprintf(stdout, "ID\tE-MAIL\n");


        for (int i = 0; i<rows; i++){
            for (int j = 0; j < columns ; j++){
                fprintf(stdout, "%s \t", PQgetvalue(Results,i,j));
            }
            fprintf(stdout, "\n");
        }

    }else if (strcmp(SELECTION, "--dump-phone") == 0){
        STATIC_SQL_COMMAND = "SELECT * FROM \"PhoneNumberID\" ";
        Results = PQexec(Connection, STATIC_SQL_COMMAND);

        rows = PQntuples(Results);
        columns = PQnfields(Results);



        fprintf(stdout, "ID\tPHONE\n");


        for (int i = 0; i<rows; i++){
            for (int j = 0; j < columns ; j++){
                fprintf(stdout, "%s \t", PQgetvalue(Results,i,j));
            }
            fprintf(stdout, "\n");
        }

    }else{
        fprintf(stderr, "[-] Invalid selection visit --help!");
        return -1 ;
    }



    PQclear(Results);
    PQfinish(Connection);


    return 0;
}

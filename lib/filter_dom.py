




if __name__ == "__main__":
    import argparse
    from .database_toolkit import DatbaseToolkit
    from .database_toolkit import ConnectionPoolTools
    from .load_config import load_config_from_file
    from .output.banner import printBanner
    from .output.consolePrint import *
    import psycopg2
    
    CONFIG = load_config_from_file()

    #? Checking config reading status 
    if not CONFIG[0]:
        sys.exit(-1)



    #? Thread size and pool size set
    ThreadSize = CONFIG[1]["service"]["thread"]
    ConnPoolSize = ThreadSize+ 5

    # ------------------ END LOAD CONFIG AND CHECK AREA ----------------------


    printBanner(CONFIG) # print current banner 



    # ------------------ BEGIN DATABASE TOOLS AND CONNECTIONS --------------------

    p_info("Initilating PostgreSQL Simple Connection pool.")
    PsqlConPool = psycopg2.pool.SimpleConnectionPool(
            maxconn=ConnPoolSize,
            minconn=ConnPoolSize,
            **CONFIG[1]["database_config"]
            )

    #? initilate database tools 
    ConnPoolTools = ConnectionPoolTools(PsqlPool=PsqlConPool)
    DatabaseTools = DatbaseToolkit(ConnPoolTools,CONFIG)

    parser = argparse.ArgumentParser()
    
    parser.add_argument("-i")
    parser.add_argument("-o")
    
    data_is = vars(parser.parse_args())
    
    in_file = data_is["i"]
    out_file = data_is["o"]
    
    
    with open(in_file, "r") as input_file:
        with open(out_file, "w+") as output_file:
            
            for line in input_file:
                if "cpanel" in line or "webmail" in line or "e-" in line or "mail" in line or "ebelediye" in line or "cpcalendars" in line or "cpcontacts" in line or "webdisk" in line:
                    continue
                else:
                    line = line.strip()
                    
                    if line.startswith("https://ww.") or line.startswith("http://ww."):
                        line = line.replace("ww.","www.")
                    
                    
                    
                    output_file.write(f"{line}\n")
    
    print("[+] Success.")
    
else:
    print(f"[!] This script not running imported!")
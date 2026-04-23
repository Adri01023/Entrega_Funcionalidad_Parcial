from sqlalchemy import create_engine, text


# Crear base de datos combinada
engine = create_engine("sqlite:///baseConjunta.db")

with engine.connect() as conn:


    conn.execute(text("PRAGMA foreign_keys = ON"))

    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS Administrador (
        id_admi INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        contrasena TEXT
    )
    """))

    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS Usuario (
        id_user INTEGER PRIMARY KEY AUTOINCREMENT,
        id_admi INTEGER,
        usuario TEXT,
        contrasena TEXT,
        FOREIGN KEY (id_admi) REFERENCES Administrador(id_admi)
            ON DELETE CASCADE ON UPDATE CASCADE
    )
    """))

    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS Futbol (
        id_jugador INTEGER PRIMARY KEY AUTOINCREMENT,
        equipo TEXT,
        jugador TEXT,
        posicion TEXT,
        partidos_jugados INTEGER,
        asistencias INTEGER,
        goles INTEGER,
        tarjetas_amarillas INTEGER,
        tarjetas_rojas INTEGER,
        id_admin INTEGER,
        FOREIGN KEY (id_admin) REFERENCES Administrador(id_admi)
            ON DELETE CASCADE ON UPDATE CASCADE
    )
    """))

    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS Empleados (
        id_empleado INTEGER PRIMARY KEY AUTOINCREMENT,
        empleado TEXT,
        departamento TEXT,
        cargo TEXT,
        salario_base INTEGER,
        salario_real INTEGER,
        fecha_contratacion DATE,
        id_admin INTEGER,
        FOREIGN KEY (id_admin) REFERENCES Administrador(id_admi)
            ON DELETE CASCADE ON UPDATE CASCADE
    )
    """))

    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS Conciertos (
        id_concierto INTEGER PRIMARY KEY AUTOINCREMENT,
        cantante TEXT,
        nacionalidad TEXT,
        fecha_nac DATE,
        concierto TEXT,
        num_canciones INTEGER,
        duracion INTEGER,
        recinto TEXT,
        pais TEXT,
        continente TEXT,
        max_entradas INTEGER,
        entradas_vendidas INTEGER,
        id_admin INTEGER,
        FOREIGN KEY (id_admin) REFERENCES Administrador(id_admi)
            ON DELETE CASCADE ON UPDATE CASCADE
    )
    """))

    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS Cine (
        id_pelicula INTEGER PRIMARY KEY AUTOINCREMENT,
        pelicula TEXT,
        genero TEXT,
        duracion INTEGER,
        presupuesto INTEGER,
        recaudacion INTEGER,
        director TEXT,
        fecha_nac_director DATE,
        actor_protagonista TEXT,
        fecha_nac_prota DATE,
        id_admin INTEGER,
        FOREIGN KEY (id_admin) REFERENCES Administrador(id_admi)
            ON DELETE CASCADE ON UPDATE CASCADE
    )
    """))



#--------------------------DATOS DE PRUEBA--------------------------------------------------------------------------------------------
    conn.execute(text("""
    INSERT OR IGNORE INTO Administrador (usuario, contrasena)
    VALUES ('ADMINISTRADOR','1234ASDF')"""))

    conn.execute(text("""
    INSERT INTO Conciertos 
    (cantante, nacionalidad, fecha_nac, concierto, num_canciones, duracion, recinto, pais, continente, max_entradas, entradas_vendidas, id_admin)
    VALUES
    ('Taylor Swift','Estadounidense','1989-12-13','1989 World Tour',19,110,'Tokyo Dome','Japón','Asia',55000,31870,1),
    ('Lorde','Neozelandesa','1996-11-07','Melodrama World Tour',20,105,'Rose Bowl Stadium','Estados Unidos','América del Norte',88000,68592,1),
    ('Coldplay','Británico','2000-01-01','A Head Full of Dreams Tour',20,105,'National Stadium Singapore','Singapur','Asia',55000,54975,1),
    ('Lorde','Neozelandesa','1996-11-07','Solar Power Tour',20,105,'Arena Corinthians','Brasil','América del Sur',49000,40027,1),
    ('Rihanna','Barbadense','1988-02-20','Anti World Tour',20,105,'Movistar Arena Madrid','España','Europa',17000,10607,1),
    ('Halsey','Estadounidense','1994-09-29','Hopeless Fountain Kingdom Tour',20,105,'National Stadium Singapore','Singapur','Asia',55000,38300,1),
    ('Rihanna','Barbadense','1988-02-20','Diamonds World Tour',20,105,'Rogers Centre','Canadá','América del Norte',50000,29654,1),
    ('Halsey','Estadounidense','1994-09-29','Manic World Tour',20,105,'WiZink Center','España','Europa',17000,12556,1),
    ('Selena Gomez','Estadounidense','1992-07-22','We Own the Night Tour',20,105,'Staples Center','Estados Unidos','América del Norte',20000,17875,1),
    ('Halsey','Estadounidense','1994-09-29','Manic World Tour',20,105,'Maracanã Stadium','Brasil','América del Sur',78000,59349,1),
    ('Selena Gomez','Estadounidense','1992-07-22','Revival Tour',20,105,'Wembley Stadium','Reino Unido','Europa',90000,52408,1),
    ('Maroon 5','Estadounidense','2000-01-01','Overexposed Tour',20,105,'Rose Bowl Stadium','Estados Unidos','América del Norte',88000,47105,1),
    ('Selena Gomez','Estadounidense','1992-07-22','Stars Dance Tour',20,105,'Arena Ciudad de México','México','América del Norte',22000,17645,1),
    ('Maroon 5','Estadounidense','2000-01-01','Overexposed Tour',20,105,'Mercedes-Benz Stadium','Estados Unidos','América del Norte',71000,45155,1),
    ('Justin Bieber','Canadiense','1994-03-01','Believe Tour',20,105,'WiZink Center','España','Europa',17000,13606,1),
    ('Taylor Swift','Estadounidense','1989-12-13','Speak Now World Tour',15,95,'WiZink Center','España','Europa',17000,11514,1),
    ('Imagine Dragons','Estadounidense','2000-01-01','Evolve World Tour',20,105,'Camp Nou','España','Europa',99000,91552,1),
    ('Dua Lipa','Británica','1995-08-22','Future Nostalgia Tour',20,105,'Arena Corinthians','Brasil','América del Sur',49000,30004,1),
    ('Justin Bieber','Canadiense','1994-03-01','Believe Tour',20,105,'Accor Arena','Francia','Europa',20000,14937,1),
    ('Dua Lipa','Británica','1995-08-22','The Self-Titled Tour',20,105,'Tokyo Dome','Japón','Asia',55000,34476,1),
    ('Harry Styles','Británico','1994-02-01','Harry Styles Live Tour',20,105,'Foro Sol','México','América del Norte',65000,38672,1),
    ('Harry Styles','Británico','1994-02-01','Harry Styles Live Tour',20,105,'River Plate Stadium','Argentina','América del Sur',83000,73572,1),
    ('Katy Perry','Estadounidense','1984-10-25','Witness Tour',20,105,'Rod Laver Arena','Australia','Oceanía',15000,10955,1)
    """))

    conn.execute(text("""
    INSERT INTO Empleados
    (empleado, departamento, cargo, salario_base, salario_real, fecha_contratacion, id_admin)
    VALUES
    ('Durant Chalker','Engineering','Gerente',3661.55,4112.55,'2005-12-05',1),
    ('Antonia Gledhill','Research and Development','soporte',1392.37,2336.37,'2022-08-06',1),
    ('Octavia Arniz','Engineering','analista',1862.03,2207.03,'2020-08-18',1),
    ('Dorisa Dunham','Training','Gerente',2538.83,3479.83,'2004-11-25',1),
    ('Eden Barnhart','Legal','analista',2167.64,2978.64,'2004-12-13',1),
    ('Nobie Tomashov','Training','soporte',4311.48,4902.48,'2012-10-09',1),
    ('Emmy Holston','Business Development','comercial',1646.74,1923.74,'2018-09-25',1),
    ('Nollie Fidal','Business Development','analista',3659.52,4601.52,'2006-07-31',1),
    ('Kim Southwick','Accounting','desarrollador',4765.38,5313.38,'2020-04-04',1),
    ('Valerye Ditchfield','Support','desarrollador',1070.06,1923.06,'2022-07-18',1),
    ('Chalmers MacLachlan','Engineering','comercial',4422.1,4564.1,'2012-05-15',1),
    ('Augie Ledgister','Research and Development','desarrollador',4875.1,5653.1,'2018-08-02',1),
    ('Cyndy Barter','Legal','soporte',4231.25,4787.25,'2021-12-13',1),
    ('Sherill Linklet','Marketing','soporte',1858.57,2752.57,'2009-02-17',1)
    """))

#--------------------------------------------------------------------------------------------------------------------------------------
    conn.commit()
    print("Base de datos creada")


# ProgBott

Discord bot for å håndtere hjelpsomme folk

## Oppsett
Prosjektet er skrevet i Python, og kan derfor kjøres nesten over alt. Jeg tilbyr også et [docker bilde](https://hub.docker.com/r/si0972/sprokfork).


<details>
    <summary>Manuelt</summary>
  
For å sette opp programvaren, må du ha Python 3,8 eller nyere.
    
    
```bash
git clone https://github.com/Roxedus/ProgBott progbott
python -m pip install -r /progbott/requirements.txt
cp /progbott/data/settings.example.json /progbott/data/settings.json
```

</details>



<details>
  <summary>Docker</summary>
  
Eksempel docker-compose.yml

```yml
  fork:
    container_name: ProgBott
    image: roxedus/progbott:latest
    networks:
      - internal
    volumes:
      - ./progbott:/app/data
```
  
</details>


Opprett en [bot-token](https://discordapp.com/developers/docs/topics/oauth2#bots), og fyll inn token-feltet i `/progbott/data/settings.json`

Du er nå klar til å starte. 
import React, {Component} from "react";
import Button from '@mui/material/Button';
import LoadingButton from '@mui/lab/LoadingButton';
import Stack from '@mui/material/Stack';
import ThreeScene from './Scene.js';
import Summary from "./Summary.js";
import SendIcon from '@mui/icons-material/Send';
import Alert from '@mui/material/Alert';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import Paper from "@mui/material/Paper";
import Container from '@mui/material/Container';
import Slider from '@mui/material/Slider';
import { styled } from "@mui/material/styles";

const testStructures = [
    {id: "532", name: "Ca2 (Cu Br2 O2)"},
    {id: "4154", name: "K2 Cu (N H C O N H C O N H)2 (H2 O)4"},
    {id: "80576", name: "Cu Sb2 O6"},
    {id: "84173", name: "Sr3 Cu3 (P O4)4"},
];

const sliderMarks = [
    {value: 4, label: '4 Å'},
    {value: 5, label: '5 Å'},
    {value: 6, label: '6 Å'},
    {value: 7, label: '7 Å'},
];

const Item = styled(Paper)(({ theme }) => ({
    backgroundColor: theme.palette.mode === "dark" ? "#1A2027" : "#fff",
    ...theme.typography.body2,
    padding: theme.spacing(1),
    textAlign: "center",
    color: theme.palette.text.secondary
  }));

class Form extends Component {

    constructor(props){
        super(props);
        this.state = {
            testStructure: "",
            testStructureId: "",
            maxR: 6,
            file: null,
            fileName: "no files selected",
            isSpinModelCalculated: false,
            loadingTestStructure: false,
            loadingUserStructure: false,  
            formula: null,
            lattice: null,
            exchanges: null,
            distances: null,
            vertices: null,
            edges: null,
            errorMessage: null,
        }
    };

    handleTestStructureChange = (event) => {
        this.setState({
            testStructure: event.target.value,
            testStructureId: event.target.value
        });
        console.log("TestStructure ", event.target);
        console.log("TestStructure ", this.state.testStructure);
    };

    handleTestStructureSubmit = () => {
        this.setState({loadingTestStructure: true});
        // assemble the responce data
        const data = new FormData();
        data.append('id', this.state.testStructureId);
        data.append('maxR', this.state.maxR);

        console.log(data);

        fetch('/process_test_cif', {
            method: 'POST',
            body: data,
            })
            .then(response => response.json())
            .then(data => { this.setState({
                formula: data.formula,
                lattice: data.lattice,
                exchanges: data.exchanges,
                distances: data.distances, 
                vertices: data.vertices,
                edges: data.edges, 
                isSpinModelCalculated: data.status, 
                errorMessage: data.error,
                loadingTestStructure: false
                });
                console.log("Submit is invoked");
                console.log(this.state);
            });

    };

    handleFileChange = (event) => {
        // add file name processing
        this.setState({
            file: event.target.files[0],
            fileName: event.target.files[0].name
        });
        
        console.log("file ", this.state);
    };

    handleFileSubmit = () => {
        // 
        this.setState({loadingUserStructure: true});

        const data = new FormData();
        // assemble the responce data
        data.append('file', this.state.file);
        data.append('maxR', this.state.maxR);
        
        fetch('/upload', {
        method: 'POST',
        body: data,
        })
        .then(response => response.json())
        .then(data => { this.setState({
            formula: data.formula,
            lattice: data.lattice,
            exchanges: data.exchanges,
            distances: data.distances, 
            vertices: data.vertices,
            edges: data.edges, 
            isSpinModelCalculated: data.status, 
            errorMessage: data.error,
            loadingUserStructure: false
            });
            console.log("Submit is invoked");
            console.log(this.state);
        });
    };

    handleSliderChange = (event, newValue) => {
        console.log('Slider change: ', newValue);
        this.setState({
            maxR: newValue,
        });
        console.log('Slider change state: ', this.state.maxR);
    };

    valuetext = (value) => {
        return `${value} Å`;
      }
      
    valueLabelFormat = (value) => {
        return sliderMarks.findIndex((mark) => mark.value === value) + 1;
      }

    render(){
        const isSpinModelCalculated = this.state.isSpinModelCalculated;

        let scene;
        let summary;
       
        if (isSpinModelCalculated) {
            scene = <ThreeScene
                        lattice={this.state.lattice}
                        exchanges={this.state.exchanges}
                        distances={this.state.distances}
                        vertices={this.state.vertices} 
                        edges={this.state.edges} />;
            summary = <Summary 
                        formula={this.state.formula}
                        exchanges={this.state.exchanges}
                        distances={this.state.distances}/>;
        } else if (this.state.errorMessage !== null) {
            scene = <p></p>
            summary = <div className="BoxWrapper">
                        <Alert severity="error" variant="filled">{this.state.errorMessage}</Alert>
                    </div>
        }

        return(
            <div className="FormWrapper">
            <Container maxWidth="lg">
            <Box sx={{ flexGrow: 1, marginBottom: 2, marginTop: 3}}>
                <Grid container spacing={2}>
                    <Grid item xs={12}>
                    <Item>
                        <Typography variant="body1" gutterBottom>
                        This application estimates transfer integral aka hopping between Cu2+ sites in undoped cuprates. 
                        Uploaded cif file should contain oxidation numbers of sites. 
                        Select one of the structures from the database as illustrative example or upload .cif file of cuprate structure from your computer.
                        </Typography>
                        <Typography variant="subtitle2" gutterBottom>
                        Maximum hopping distance
                        </Typography>
                        <Stack spacing={2} direction="row" justifyContent="center">
                        <Box sx={{ width: 300 }}>
                        <Slider
                            aria-label="Restricted values"
                            value={this.state.maxR}
                            onChange={this.handleSliderChange}
                            getAriaValueText={this.valuetext}
                            step={0.5}
                            min={4}
                            max={7}
                            valueLabelDisplay="auto"
                            marks={sliderMarks}/>
                        </Box>
                        </Stack>
                    </Item>
                    </Grid>
                    <Grid item xs={6}>
                    <Item>
                        <Typography variant="subtitle1" gutterBottom>
                        Use structure from database
                        </Typography>
                        <Stack spacing={2} direction="row" justifyContent="center">
                        <FormControl sx={{ minWidth: 300 }} size="small">
                        <InputLabel id="structure-select">Select Cuprate</InputLabel>
                        <Select
                            labelId="structure-select"
                            id="structure-select"
                            value={this.state.testStructureId}
                            label="Test structure"
                            onChange={this.handleTestStructureChange}>
                            {testStructures.map((structure) => (
                                <MenuItem
                                key={structure.id}
                                value={structure.id}>
                                {structure.name}
                                </MenuItem>
                            ))}
                        </Select>
                        </FormControl>
                        <LoadingButton
                            size="medium"
                            disabled={this.state.testStructure === '' || this.state.loadingUserStructure}
                            onClick={this.handleTestStructureSubmit}
                            endIcon={<SendIcon />}
                            loading={this.state.loadingTestStructure}
                            loadingPosition="end"
                            variant="contained">
                            Process
                        </LoadingButton>
                        </Stack>
                    </Item>
                    </Grid>
                    <Grid item xs={6}>
                    <Item>
                        <Typography variant="subtitle1" gutterBottom>
                        Upload my cif file
                        </Typography>
                        <Container>
                        <Stack spacing={2} direction="row" justifyContent="center">
                        <input 
                            type="file" 
                            id="file-upload" 
                            onChange={this.handleFileChange} 
                            style={{display: "none"}} 
                            accept=".cif"/>
                        <label className="uploadButton" htmlFor="file-upload">
                        <Button 
                            variant="text" 
                            component="span"
                            size="medium">
                            Select cif
                        </Button>
                        </label>
                        <p className="TruncatedText">{this.state.fileName}</p>
                        <LoadingButton
                            size="medium"
                            disabled={this.state.file === null || this.state.loadingTestStructure}
                            onClick={this.handleFileSubmit}
                            endIcon={<SendIcon />}
                            loading={this.state.loadingUserStructure}
                            loadingPosition="end"
                            variant="contained">
                            Send cif
                        </LoadingButton>
                    </Stack>
                    </Container>
                    </Item>
                    </Grid>
                </Grid>
                </Box>

                {scene}
                {summary}
            </Container>
            </div>
        )
    };
}

export default Form;
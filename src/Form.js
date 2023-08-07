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
import parse from 'html-react-parser';
import { styled } from "@mui/material/styles";

const testStructures = [
    {id: "haydeeite", name: "Cu3 Mg (OH)6 Cl2"},
    {id: "kapellasite", name: "Cu3 Zn (OH)6 Cl2"},
    {id: "linarite", name: "Pb Cu SO4 (OH)2"},
    {id: "La2CuO4", name: "La2 Cu O4"},
    {id: "SrCu2O3", name: "Sr Cu2 O3"},
    {id: "CuSe2O5", name: "Cu Se2 O5"},
    {id: "CuTe2O5", name: "Cu Te2 O5"},
    {id: "Bi2CuO4", name: "Bi2 Cu O4"},
    {id: "Bi2Sr2CuO6", name: "Bi2 Sr2 Cu O6"},
    {id: "HgBa2CuO4", name: "Hg Ba2 Cu O4"},
    {id: "HgBa2CaCu2O6", name: "Hg Ba2 Ca Cu2 O6"},
    {id: "HgBa2Ca2Cu3O8", name: "Hg Ba2 Ca2 Cu3 O8"},
    {id: "Tl2Ba2CuO6", name: "Tl2 Ba2 Cu O6"},
    {id: "Tl2Ba2CaCu2O8", name: "Tl2 Ba2 Ca Cu2 O8"},
    {id: "Tl2Ba2Ca2Cu3O10", name: "Tl2 Ba2 Ca2 Cu3 O10"},
];

const sliderMarks = [
    {value: 4, label: '4 Å'},
    {value: 5, label: '5 Å'},
    {value: 6, label: '6 Å'},
    {value: 7, label: '7 Å'},
    {value: 8, label: '8 Å'},
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
        // console.log("TestStructure ", event.target);
        // console.log("TestStructure ", this.state.testStructure);
    };

    handleTestStructureSubmit = () => {
        this.setState({loadingTestStructure: true});
        // assemble the responce data
        const data = new FormData();
        data.append('id', this.state.testStructureId);
        data.append('maxR', this.state.maxR);

        // console.log(data);

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
                // console.log("Submit is invoked");
                // console.log(this.state);
            });

    };

    handleFileChange = (event) => {
        // add file name processing
        this.setState({
            file: event.target.files[0],
            fileName: event.target.files[0].name
        });
        
        // console.log("file ", this.state);
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
            // console.log("Submit is invoked");
            // console.log(this.state);
        });
    };

    handleSliderChange = (event, newValue) => {
        // console.log('Slider change: ', newValue);
        this.setState({
            maxR: newValue,
        });
        // console.log('Slider change state: ', this.state.maxR);
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
                        This application estimates leading transfer integrals in S=1/2 magnetic insulators with Cu{parse("<sup>2+<sup/>")} (undoped cuprates). 
                        You can select a structure from the dropdown list or upload a CIF-file of your own structure. 
                        (The latter must contain information on the oxidation states of the atoms). 
                        Note that a calculation can take up to a few minutes for involved structures and large cutoff distances (defined by the slider). 
                        As a rule of thumb, the calculation of one transfer integral takes about 3 seconds.
                        </Typography>
                        <Typography variant="subtitle2" gutterBottom>
                        Maximum Cu-Cu distance
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
                            max={8}
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
                                <Typography variant="subtitle2" gutterBottom>
                                {parse(structure.name.replaceAll(/\d+/g, "<sub>$&</sub>"))}
                                </Typography>
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
                        Upload CIF-file
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
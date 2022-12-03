import React, {Component} from "react";
import Button from '@mui/material/Button';
import LoadingButton from '@mui/lab/LoadingButton';
import Stack from '@mui/material/Stack';
import ThreeScene from './Scene.js';
import Summary from "./Summary.js";
import SendIcon from '@mui/icons-material/Send';
import Alert from '@mui/material/Alert';

class Form extends Component {

    constructor(props){
        super(props);
        this.state = {
            file: null,
            isSpinModelCalculated: false,
            loading: false, 
            fileName: "no files selected yet",
            formula: null,
            lattice: null,
            exchanges: null,
            distances: null,
            vertices: null,
            edges: null,
            errorMessage: null
        }
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
        this.setState({loading: true});

        const data = new FormData();
        // assemble the responce data
        data.append('file', this.state.file);
        
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
            loading: false
            });
            console.log("Submit is invoked");
            console.log(this.state);
        });
    };

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
                        distances={this.state.distances}
                        />;
        } else if (this.state.errorMessage !== null) {
            scene = <p></p>
            summary = <div className="BoxWrapper">
                        <Alert severity="error" variant="filled">{this.state.errorMessage}</Alert>
                    </div>
        }

        return(
            <div className="FormWrapper">
                
                <div className="BoxWrapper">
                    <div className="TextBox">
                        <p>This application estimates transfer integrals between Cu2+ sites in undoped cuprates. Uploaded cif file should contain oxidation numbers of sites.</p>
                        <p>Select .cif file of cuprate structure you are interested in.</p>
                    </div>
                </div>

                <div className="BoxWrapper">
                    <Stack spacing={2} direction="row">
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
                            disabled={this.state.file === null || this.state.isUploadPending}
                            onClick={this.handleFileSubmit}
                            endIcon={<SendIcon />}
                            loading={this.state.loading}
                            loadingPosition="end"
                            variant="contained">
                            Send cif
                        </LoadingButton>
                    </Stack>
                </div>

                {scene}
                {summary}

            </div>
        )
    };
}

export default Form;
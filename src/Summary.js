import React, { Component } from "react";
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import Brightness1Icon from '@mui/icons-material/Brightness1';
import ExchangeColors from "./declarations.js"
import parse from 'html-react-parser';

class Summary extends Component {

    createData = (
        index,
        color,
        exchange,
        distance,
      ) => { return {index, color, exchange, distance}; }
    
    makeRows = () => {
        let rows = [];

        for (let i = 0; i < this.props.exchanges.length; i++){
            rows.push(this.createData(i, ExchangeColors[i], this.props.exchanges[i], this.props.distances[i]))
        }
        return rows;
    }

    formatChemFormula = (formula) => {
        return formula.replaceAll(/\d+/g, "<sub>$&</sub>");
    }

    render(){
        console.log(this.props)
        return(
            <div className="summaryWrapper">
                <p>{parse(this.formatChemFormula(this.props.formula))}, number of determined transfer integrals: {this.props.exchanges.length}</p>
                <TableContainer component={Paper}>
                    <Table sx={{ minWidth: 400 }} size="small" aria-label="a dense table">
                        <TableHead>
                        <TableRow>
                            <TableCell>Index</TableCell>
                            <TableCell align="center">Color</TableCell>
                            <TableCell align="right">Hoping, meV</TableCell>
                            <TableCell align="right">Distance, Ang</TableCell>
                        </TableRow>
                        </TableHead>
                        <TableBody>
                        {this.makeRows().map((row) => (
                            <TableRow
                            key={row.index}
                            sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                            >
                            <TableCell component="th" scope="row">
                                {row.index}
                            </TableCell>
                            <TableCell align="center"><Brightness1Icon sx={{ color: row.color }}/></TableCell>
                            <TableCell align="right">{row.exchange}</TableCell>
                            <TableCell align="right">{row.distance}</TableCell>
                            </TableRow>
                        ))}
                        </TableBody>
                    </Table>
                    </TableContainer>
            </div>
        )
    };
}

export default Summary;
<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class DebugController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        //
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        //
    }

    /**
     * Display the specified resource.
     */
    public function show(string $id)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, string $id)
    {
        //
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(string $id)
    {
        //
    }

    /**
     * Debug the incoming request
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\Response
     */
    public function debug(Request $request)
    {
        return response()->json([
            'headers' => $request->headers->all(),
            'body' => $request->all(),
            'method' => $request->method(),
            'path' => $request->path(),
            'url' => $request->url(),
            'server_info' => [
                'host' => gethostname(),
                'ip' => gethostbyname(gethostname()),
                'php_version' => PHP_VERSION,
                'laravel_version' => app()->version(),
            ]
        ]);
    }
}
